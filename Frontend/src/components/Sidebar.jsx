import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";

const Sidebar = () => {
  const { logout } = useAuth();
  const { t } = useLanguage();

  return (
    <div className="flex">
      <nav
        className="sticky top-0 h-screen w-72 bg-white border-r border-neutral-200/20 flex-shrink-0 hidden lg:block">
        <div className="p-5 border-b border-neutral-200/20">
          <h1 className="text-xl font-bold text-neutral-800">AigesX</h1>
          <span className="text-sm text-neutral-500">Fuzzing-as-a-Service</span>
        </div>

        <div className="py-4">
          <NavLink to="/dashboard" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            {t("commandCenter")}
          </NavLink>

          <NavLink to="/intake" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 3v12"></path>
              <path d="m7 10 5-5 5 5"></path>
              <path d="M5 21h14"></path>
            </svg>
            {t("targetIntake")}
          </NavLink>

          <NavLink to="/settings" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 15.5A3.5 3.5 0 1 0 12 8.5a3.5 3.5 0 0 0 0 7z"></path>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.01A1.65 1.65 0 0 0 10 3.09V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.01a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.01a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            {t("settings")}
          </NavLink>

          <NavLink to="/reports" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M8 6h13"></path>
              <path d="M8 12h13"></path>
              <path d="M8 18h13"></path>
              <path d="M3 6h.01"></path>
              <path d="M3 12h.01"></path>
              <path d="M3 18h.01"></path>
            </svg>
            {t("reports")}
          </NavLink>
        </div>
        <div className="absolute bottom-0 w-full p-4 border-t border-neutral-200/20">
          <div className="flex items-center justify-between">
            <p className="text-xs text-neutral-500">{t("secureWorkspace")}</p>
            <button onClick={logout} className="text-sm text-neutral-600 hover:text-neutral-800">{t("logout")}</button>
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;
