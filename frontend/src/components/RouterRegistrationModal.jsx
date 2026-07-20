import {
  Eye,
  EyeOff,
  LoaderCircle,
  Router,
  X,
} from "lucide-react";
import { useState } from "react";

import { routerService } from "../services/routerService";


const INITIAL_FORM = {
  name: "",
  managementIp: "",
  publicIp: "",
  apiPort: "8729",
  username: "",
  password: "",
};


function validateForm(formData) {
  const errors = {};

  if (!formData.name.trim()) {
    errors.name = "Router name is required.";
  }

  if (!formData.managementIp.trim()) {
    errors.managementIp =
      "Management IP is required.";
  }

  const apiPort = Number(formData.apiPort);

  if (
    !Number.isInteger(apiPort)
    || apiPort < 1
    || apiPort > 65_535
  ) {
    errors.apiPort =
      "Enter a valid TCP port.";
  }

  if (!formData.username.trim()) {
    errors.username = "Username is required.";
  }

  if (!formData.password) {
    errors.password = "Password is required.";
  }

  return errors;
}


function FormField({
  label,
  name,
  value,
  error,
  required = false,
  helperText,
  children,
  ...inputProps
}) {
  const inputId = `router-${name}`;

  return (
    <div>
      <label
        htmlFor={inputId}
        className="mb-2 block text-sm font-medium text-slate-300"
      >
        {label}

        {required && (
          <span className="ml-1 text-emerald-400">
            *
          </span>
        )}
      </label>

      {children ?? (
        <input
          id={inputId}
          name={name}
          value={value}
          className={[
            "h-11 w-full rounded-xl border bg-slate-950/70 px-3",
            "text-sm text-white outline-none transition",
            "placeholder:text-slate-600",
            error
              ? "border-red-400/40 focus:border-red-400"
              : "border-white/10 focus:border-emerald-400/50",
          ].join(" ")}
          {...inputProps}
        />
      )}

      {error ? (
        <p className="mt-1.5 text-xs text-red-300">
          {error}
        </p>
      ) : helperText ? (
        <p className="mt-1.5 text-xs leading-5 text-slate-600">
          {helperText}
        </p>
      ) : null}
    </div>
  );
}


export function RouterRegistrationModal({
  isOpen,
  onClose,
  onCreated,
}) {
  const [formData, setFormData] =
    useState(INITIAL_FORM);

  const [fieldErrors, setFieldErrors] =
    useState({});

  const [serverError, setServerError] =
    useState(null);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [showPassword, setShowPassword] =
    useState(false);

  if (!isOpen) {
    return null;
  }

  function updateField(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));

    setFieldErrors((current) => ({
      ...current,
      [name]: undefined,
    }));

    setServerError(null);
  }

  function resetModal() {
    setFormData(INITIAL_FORM);
    setFieldErrors({});
    setServerError(null);
    setShowPassword(false);
  }

  function handleClose() {
    if (isSubmitting) {
      return;
    }

    resetModal();
    onClose();
  }

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const validationErrors =
      validateForm(formData);

    if (
      Object.keys(validationErrors).length > 0
    ) {
      setFieldErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    setServerError(null);

    try {
      const router = await routerService.create({
        name: formData.name.trim(),
        management_ip:
          formData.managementIp.trim(),
        public_ip:
          formData.publicIp.trim() || null,
        api_port: Number(formData.apiPort),
        username: formData.username.trim(),
        password: formData.password,
      });

      resetModal();
      onClose();
      onCreated?.(router);
    } catch (error) {
      setServerError(
        error?.message
          ?? "The router could not be registered.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      role="presentation"
      onMouseDown={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm"
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="router-registration-title"
        className="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-2xl border border-white/10 bg-slate-900 shadow-2xl shadow-black/50"
      >
        <header className="flex items-start justify-between border-b border-white/[0.07] px-5 py-5 sm:px-6">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-emerald-400/20 bg-emerald-400/10">
              <Router className="size-5 text-emerald-400" />
            </div>

            <div>
              <h2
                id="router-registration-title"
                className="font-semibold text-white"
              >
                Register MikroTik router
              </h2>

              <p className="mt-1 text-sm leading-5 text-slate-500">
                ARGOS will validate the RouterOS API-SSL
                connection before saving the device.
              </p>
            </div>
          </div>

          <button
            type="button"
            aria-label="Close router registration"
            disabled={isSubmitting}
            onClick={handleClose}
            className="flex size-9 shrink-0 items-center justify-center rounded-xl text-slate-500 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            <X className="size-5" />
          </button>
        </header>

        <form onSubmit={handleSubmit}>
          <div className="space-y-5 p-5 sm:p-6">
            {serverError && (
              <div className="rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3">
                <p className="text-sm font-medium text-red-200">
                  Router registration failed
                </p>

                <p className="mt-1 text-xs leading-5 text-red-300/80">
                  {serverError}
                </p>
              </div>
            )}

            <div className="grid gap-5 sm:grid-cols-2">
              <FormField
                label="Router name"
                name="name"
                type="text"
                required
                autoFocus
                value={formData.name}
                error={fieldErrors.name}
                onChange={updateField}
                placeholder="Matriz Recife"
              />

              <FormField
                label="Management IP"
                name="managementIp"
                type="text"
                required
                value={formData.managementIp}
                error={fieldErrors.managementIp}
                onChange={updateField}
                placeholder="10.200.0.21"
                helperText="Private IP reachable through the WireGuard network."
              />

              <FormField
                label="Public IP"
                name="publicIp"
                type="text"
                value={formData.publicIp}
                error={fieldErrors.publicIp}
                onChange={updateField}
                placeholder="Optional"
                helperText="Inventory information only. It is not used for management."
              />

              <FormField
                label="RouterOS API port"
                name="apiPort"
                type="number"
                required
                min="1"
                max="65535"
                value={formData.apiPort}
                error={fieldErrors.apiPort}
                onChange={updateField}
                placeholder="8729"
              />

              <FormField
                label="Username"
                name="username"
                type="text"
                required
                autoComplete="username"
                value={formData.username}
                error={fieldErrors.username}
                onChange={updateField}
                placeholder="argos-api"
              />

              <FormField
                label="Password"
                name="password"
                required
                value={formData.password}
                error={fieldErrors.password}
              >
                <div className="relative">
                  <input
                    id="router-password"
                    name="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    required
                    autoComplete="new-password"
                    value={formData.password}
                    onChange={updateField}
                    placeholder="RouterOS password"
                    className={[
                      "h-11 w-full rounded-xl border bg-slate-950/70 px-3 pr-11",
                      "text-sm text-white outline-none transition",
                      "placeholder:text-slate-600",
                      fieldErrors.password
                        ? "border-red-400/40 focus:border-red-400"
                        : "border-white/10 focus:border-emerald-400/50",
                    ].join(" ")}
                  />

                  <button
                    type="button"
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    onClick={() => {
                      setShowPassword(
                        (current) => !current,
                      );
                    }}
                    className="absolute right-1 top-1 flex size-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-white/5 hover:text-slate-300"
                  >
                    {showPassword ? (
                      <EyeOff className="size-4" />
                    ) : (
                      <Eye className="size-4" />
                    )}
                  </button>
                </div>
              </FormField>
            </div>

            <div className="rounded-xl border border-amber-400/10 bg-amber-400/5 px-4 py-3">
              <p className="text-xs leading-5 text-amber-200/70">
                The password is sent only to the ARGOS
                backend and encrypted before being stored.
                It is never returned through API responses.
              </p>
            </div>
          </div>

          <footer className="flex flex-col-reverse gap-3 border-t border-white/[0.07] px-5 py-4 sm:flex-row sm:justify-end sm:px-6">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={handleClose}
              className="h-10 rounded-xl border border-white/10 px-4 text-sm font-medium text-slate-300 transition hover:border-white/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex h-10 items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle className="size-4 animate-spin" />
                  Validating connection...
                </>
              ) : (
                <>
                  <Router className="size-4" />
                  Register router
                </>
              )}
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
}