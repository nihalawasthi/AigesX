import json
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import lightgbm as lgb
import joblib
from concurrent.futures import ThreadPoolExecutor
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnhancedCVETrainer:
    def __init__(self, data_dir="C:/My/Projects/_Python/AigesX/cve_data/NVD/", models_dir="C:/My/Projects/_Python/AigesX/models/"):
        self.data_dir = data_dir
        self.models_dir = models_dir
        self.text_vectorizer = HashingVectorizer(n_features=2**18, ngram_range=(1, 2))
        self.ct = None
        self.label_encoder = LabelEncoder()
        self.model = None
        
        os.makedirs(self.models_dir, exist_ok=True)
        self._create_feature_pipeline()

    def _create_feature_pipeline(self):
        """Create optimized feature transformation pipeline"""
        self.ct = ColumnTransformer([
            ('text', self.text_vectorizer, 'combined_text'),
            ('cwe', OneHotEncoder(handle_unknown='ignore', max_categories=100), ['cwe_category']),
            ('cvss', 'passthrough', ['cvss_score', 'exploitability_score', 'impact_score']),
            ('temporal', 'passthrough', ['years_since_published']),
            ('attack', OneHotEncoder(handle_unknown='ignore'), ['attack_vector'])
        ], remainder='drop', n_jobs=-1)

    def _process_cpe(self, cpe23uri):
        """Parse CPE URI into components with validation"""
        try:
            parts = re.match(r'cpe:2\.3:[a-z]:([^:]+):([^:]+)', cpe23uri)
            if not parts:
                return {'vendor': 'unknown', 'product': 'unknown'}
            return {
                'vendor': parts.group(1).lower(),
                'product': parts.group(2).lower()
            }
        except Exception as e:
            logging.debug(f"CPE parsing error: {str(e)}")
            return {'vendor': 'unknown', 'product': 'unknown'}

    def _safe_get(self, data, keys, default=None):
        """Safely navigate nested dictionaries"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def _extract_features(self, item):
        """Robust feature extraction with comprehensive validation"""
        try:
            cve_id = self._safe_get(item, ['cve', 'CVE_data_meta', 'ID'], 'CVE-UNKNOWN')
            
            try:
                published = datetime.fromisoformat(item['publishedDate'].rstrip('Z'))
                years_since = (datetime.now() - published).days / 365
            except:
                years_since = 10.0
            descriptions = self._safe_get(item, ['cve', 'description', 'description_data'], [])
            description = ' '.join([desc.get('value', '') for desc in descriptions 
                                if isinstance(desc, dict) and desc.get('lang') == 'en'])

            problemtype = self._safe_get(item, ['cve', 'problemtype', 'problemtype_data'], [{}])
            cwe_entry = None
            
            if problemtype and isinstance(problemtype[0], dict):
                descriptions = problemtype[0].get('description', [{}])
                if descriptions and isinstance(descriptions[0], dict):
                    cwe_entry = descriptions[0].get('value', 'CWE-OTHER')
            
            cwe_category = cwe_entry.split('-')[-1] if cwe_entry and '-' in cwe_entry else 'other'

            metrics = item.get('impact', {})
            cvss_v3 = metrics.get('baseMetricV3', {}).get('cvssV3', {})
            cvss_v2 = metrics.get('baseMetricV2', {}).get('cvssV2', {})
            
            cvss_score = float(cvss_v3.get('baseScore', cvss_v2.get('baseScore', 5.0)))
            exploitability = float(metrics.get('baseMetricV3', {}).get('exploitabilityScore', 
                            metrics.get('baseMetricV2', {}).get('exploitabilityScore', 3.0)))
            impact_score = float(metrics.get('baseMetricV3', {}).get('impactScore', 
                        metrics.get('baseMetricV2', {}).get('impactScore', 3.0)))
            
            attack_vector = cvss_v3.get('attackVector', 
                        cvss_v2.get('accessVector', 'NETWORK')).upper()

            cpe_uris = []
            nodes = self._safe_get(item, ['configurations', 'nodes'], [])
            
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                    
                cpe_matches = node.get('cpe_match', [])
                for cpe in cpe_matches:
                    if isinstance(cpe, dict) and cpe.get('vulnerable', False):
                        uri = cpe.get('cpe23Uri', '')
                        if uri.startswith('cpe:2.3:'):
                            cpe_uris.append(uri)

            cpe_analysis = [self._process_cpe(uri) for uri in cpe_uris]
            vendors = list(set([cpe['vendor'] for cpe in cpe_analysis if cpe]))
            products = list(set([cpe['product'] for cpe in cpe_analysis if cpe]))
            
            if not cpe_uris:
                vendors = ['unknown']
                products = ['unknown']

            references = self._safe_get(item, ['cve', 'references', 'reference_data'], [])
            ref_count = len(references) if isinstance(references, list) else 0

            return {
                'cve_id': cve_id,
                'description': description,
                'cwe_category': cwe_category,
                'severity': self._safe_get(cvss_v3, ['baseSeverity'], 
                        self._safe_get(cvss_v2, ['severity'], 'MEDIUM')).upper(),
                'cvss_score': cvss_score,
                'exploitability_score': exploitability,
                'impact_score': impact_score,
                'attack_vector': attack_vector,
                'vendors': ' '.join(vendors),
                'products': ' '.join(products),
                'references_count': ref_count,
                'years_since_published': years_since,
                'combined_text': f"{description} {' '.join(vendors)} {' '.join(products)}"
            }
        except Exception as e:
            logging.error(f"Error processing CVE {cve_id}: {str(e)}")
            return None

    def load_data(self):
        """Optimized data loading with batch processing"""
        cve_data = []
        files = [f for f in os.listdir(self.data_dir) if f.startswith('nvdcve-1.1-')]
        
        with ThreadPoolExecutor(max_workers=os.cpu_count()//2) as executor:
            for file in sorted(files):
                file_path = os.path.join(self.data_dir, file)
                logging.info(f"Processing {file_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results = list(executor.map(self._extract_features, data['CVE_Items']))
                        valid_results = [r for r in results if r is not None]
                        cve_data.extend(valid_results)
                        logging.info(f"Processed {len(valid_results)} entries from {file}")
                        
                except Exception as e:
                    logging.error(f"Error processing file {file}: {str(e)}")
        
        return pd.DataFrame(cve_data)

    def train(self):
        """Training process with validation"""
        try:
            logging.info("Loading and processing data...")
            df = self.load_data()
            
            if df.empty:
                raise ValueError("No valid CVE data found")
            
            logging.info(f"Loaded {len(df)} valid CVE records")
            
            logging.info("Encoding labels...")
            y = self.label_encoder.fit_transform(df['severity'])
            
            logging.info("Transforming features...")
            X = self.ct.fit_transform(df)
            
            logging.info("Training LightGBM model...")
            self.model = lgb.LGBMClassifier(
                num_leaves=31,
                max_depth=-1,
                learning_rate=0.1,
                n_estimators=500,
                n_jobs=-1,
                class_weight='balanced',
                verbosity=-1
            )
            self.model.fit(X, y)
            
            logging.info("Saving model artifacts...")
            joblib.dump({
                'model': self.model,
                'column_transformer': self.ct,
                'label_encoder': self.label_encoder
            }, os.path.join(self.models_dir, 'aigesx_cve_model_v2.pkl'))
            
            logging.info("Training completed successfully!")
            
        except KeyboardInterrupt:
            logging.info("Training interrupted by user")
        except Exception as e:
            logging.error(f"Training failed: {str(e)}")
            raise

if __name__ == "__main__":
    trainer = EnhancedCVETrainer()
    trainer.train()