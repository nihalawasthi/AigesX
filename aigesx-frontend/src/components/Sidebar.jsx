import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import logo from "../assets/react.svg"; 


const Sidebar = () => {
  const { logout } = useAuth();
  const userEmail = "nihalawasthi498@gmail.com";

  return (
    <div className="flex">
      <nav
        className="sticky top-0 h-screen w-64 bg-white border-r border-neutral-200/20 flex-shrink-0 hidden lg:block">
        <div className="p-4 border-b border-neutral-200/20">
          <h1 className="text-xl font-bold">AigesX</h1>
          <span className="text-sm text-neutral-500">v0.0</span>
        </div>

        <div className="py-4">
          <Link to="#" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            Dashboard
          </Link>

          <Link to="#vulnerabilities" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            Vulnerabilities
          </Link>

          <Link to="#analytics" className="flex items-center px-4 py-2 text-neutral-600 hover:bg-neutral-100">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            Analytics
          </Link>
        </div>
        <div className="absolute bottom-0 w-full p-4 border-t border-neutral-200/20">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-neutral-200">
              <img src={logo} alt="User Logo" className="w-full h-full object-cover" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">{userEmail}</p>
              <button onClick={logout} className="text-sm text-neutral-500 hover:text-neutral-700">Logout</button>
            </div>
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;
