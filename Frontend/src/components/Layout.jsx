import { Link } from "react-router-dom";
import Sidebar from "./Sidebar";
import logo from "../assets/react.svg"; // Make sure the logo is available

const Layout = ({ children }) => {
  return (
    <div id="Layout" className="min-h-screen bg-[#E5E7EB] flex">
      <Sidebar />

     <main className="flex-1 overflow-auto">
        {/* <header className="sticky top-0 z-10 bg-white border-b border-neutral-200/20 px-4 py-3">
          <div className="flex items-center justify-between">
            <button className="lg:hidden p-2 rounded-lg hover:bg-neutral-100">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>

            <div className="flex-1 px-4">
              <input type="search" placeholder="Search..." className="w-full max-w-md px-4 py-2 rounded-lg border border-neutral-200/20 bg-neutral-50" />
            </div>

            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg hover:bg-neutral-100">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                </svg>
              </button>

              <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-neutral-200 overflow-hidden">
                  <img src={logo} alt="User Logo" className="w-full h-full object-cover" />
                </div>
              </div>
            </div>
          </div>
        </header> */}

        <div className="p-6">{children}</div>
      </main>
    </div>
  );
};

export default Layout;
