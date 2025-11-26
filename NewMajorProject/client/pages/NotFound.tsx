import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Link } from "react-router-dom";
import Header from "@/components/ui/Header";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background dark">
      <Header />
      <div className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
        <div className="text-center max-w-2xl">
          <div className="mb-8">
            <h1 className="text-7xl font-bold bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent mb-4">
              404
            </h1>
            <p className="text-2xl font-bold text-foreground mb-2">
              Page Not Found
            </p>
            <p className="text-lg text-muted-foreground">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8">
            <Link
              to="/"
              className="relative px-8 py-3 font-semibold text-background rounded-lg overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover:opacity-90 transition-opacity" />
              <span className="relative">Return Home</span>
            </Link>

            <Link
              to="/dashboard"
              className="px-8 py-3 font-semibold text-foreground border border-neon-cyan/50 rounded-lg hover:bg-neon-cyan/10 transition-colors"
            >
              Go to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
