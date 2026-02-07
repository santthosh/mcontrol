import { ConnectionStatus } from "./components/ConnectionStatus";

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">
            Mission Control
          </h1>
          <ConnectionStatus />
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🚀</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to Mission Control
          </h2>
          <p className="text-gray-600 max-w-md">
            Your desktop command center for managing long-running AI agents.
            Connect, monitor, and orchestrate your AI workforce.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white px-4 py-2">
        <p className="text-xs text-gray-400 text-center">
          Mission Control v0.0.1
        </p>
      </footer>
    </div>
  );
}

export default App;
