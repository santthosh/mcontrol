import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export function UserMenu() {
  const { user, signOut } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  if (!user) return null;

  const initials = (user.displayName || user.email)
    .split(/[\s@]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0].toUpperCase())
    .join("");

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="flex items-center gap-2 hover:bg-gray-100 rounded-full p-0.5 transition-colors"
        title={user.email}
      >
        {user.avatarUrl ? (
          <img
            src={user.avatarUrl}
            alt=""
            className="h-7 w-7 rounded-full"
            referrerPolicy="no-referrer"
          />
        ) : (
          <div className="h-7 w-7 rounded-full bg-primary-600 flex items-center justify-center">
            <span className="text-xs font-medium text-white">{initials}</span>
          </div>
        )}
      </button>

      {showMenu && (
        <>
          {/* Backdrop to close menu */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          />
          <div className="absolute top-full right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 w-64">
            <div className="p-3 border-b border-gray-100">
              {user.displayName && (
                <div className="text-sm font-medium text-gray-900">
                  {user.displayName}
                </div>
              )}
              <div className="text-xs text-gray-500 truncate">
                {user.email}
              </div>
            </div>
            <div className="p-1">
              <button
                onClick={() => {
                  setShowMenu(false);
                  signOut();
                }}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              >
                Sign out
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
