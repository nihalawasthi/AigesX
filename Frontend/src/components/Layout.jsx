import Sidebar from "./Sidebar";

const Layout = ({ children }) => {
  return (
    <div id="Layout" className="min-h-screen bg-gradient-to-b from-[#f7f8fb] to-[#eef1f6] flex">
      <Sidebar />

     <main className="flex-1 overflow-auto">
        <div className="max-w-[1200px] mx-auto py-6">{children}</div>
      </main>
    </div>
  );
};

export default Layout;
