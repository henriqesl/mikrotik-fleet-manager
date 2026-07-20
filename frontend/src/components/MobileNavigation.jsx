import {
  Activity,
  LayoutDashboard,
  Router,
  Settings,
  ShieldCheck,
  X,
} from "lucide-react";
import { useEffect } from "react";


const navigationItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    active: true,
  },
  {
    label: "Routers",
    icon: Router,
    active: false,
  },
  {
    label: "Monitoring",
    icon: Activity,
    active: false,
  },
  {
    label: "Settings",
    icon: Settings,
    active: false,
  },
];


export function MobileNavigation({
  isOpen,
  onClose,
}) {
  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow = "hidden";

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      document.body.style.overflow =
        previousOverflow;

      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }

  return (
    <div
      role="presentation"
      onMouseDown={handleBackdropClick}
      className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm lg:hidden"
    >
      <aside className="flex h-full w-72 max-w-[85vw] flex-col border-r border-white/10 bg-slate-950 px-4 py-5 shadow-2xl shadow-black/60">
        <header className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <img
              src="/argos-mark.svg"
              alt=""
              className="size-10"
            />

            <div>
              <p className="text-sm font-semibold tracking-[0.22em] text-white">
                ARGOS
              </p>

              <p className="text-xs text-slate-500">
                MikroTik Fleet Manager
              </p>
            </div>
          </div>

          <button
            type="button"
            aria-label="Close navigation"
            onClick={onClose}
            className="flex size-9 items-center justify-center rounded-xl text-slate-500 transition hover:bg-white/5 hover:text-white"
          >
            <X className="size-5" />
          </button>
        </header>

        <nav className="mt-10 space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.label}
                type="button"
                onClick={onClose}
                className={[
                  "flex w-full items-center gap-3 rounded-xl px-3 py-2.5",
                  "text-sm font-medium transition",
                  item.active
                    ? "bg-emerald-400/10 text-emerald-300"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-100",
                ].join(" ")}
              >
                <Icon className="size-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="mt-auto rounded-2xl border border-emerald-400/10 bg-emerald-400/5 p-4">
          <div className="flex items-center gap-2 text-emerald-300">
            <ShieldCheck className="size-4" />

            <span className="text-xs font-semibold uppercase tracking-wider">
              Secure network
            </span>
          </div>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            Router management is restricted to the
            private WireGuard network.
          </p>
        </div>
      </aside>
    </div>
  );
}