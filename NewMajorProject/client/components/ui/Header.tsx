import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

export default function Header() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative">
              <div className="absolute inset-0 bg-neon-cyan rounded-lg blur opacity-40 group-hover:opacity-60 transition-opacity" />
              <div className="relative bg-gradient-to-br from-neon-cyan to-neon-blue px-3 py-2 rounded-lg">
                <span className="text-foreground font-bold text-lg">CROWD</span>
              </div>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link
              to="/"
              className={cn(
                "text-sm font-medium transition-colors",
                isActive("/")
                  ? "text-neon-cyan"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Home
            </Link>
            <Link
              to="/about"
              className={cn(
                "text-sm font-medium transition-colors",
                isActive("/about")
                  ? "text-neon-cyan"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              About
            </Link>
            <Link
              to="/dashboard"
              className={cn(
                "text-sm font-medium transition-colors",
                isActive("/dashboard")
                  ? "text-neon-cyan"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Dashboard
            </Link>
          </nav>

          {/* Auth Buttons */}
          <div className="flex items-center gap-4">
            <button className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Sign In
            </button>
            <button className="relative px-6 py-2 font-medium text-background rounded-lg overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover:opacity-90 transition-opacity" />
              <span className="relative">Sign Up</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
