export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 p-4 dark:bg-zinc-900">
      <div className="w-full max-w-5xl flex flex-col items-center">
        <div className="flex justify-center mb-8">
          {/* Logo */}
          <div className="flex flex-row items-center gap-4">
            <div className="rounded-full bg-orange-400 p-2">
              <svg
                className="icon-white"
                viewBox="0 0 24 24"
                style={{ width: "30px", height: "30px" }}
                aria-label="Mealie logo"
              >
                <path
                  fill="currentColor"
                  d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
                />
              </svg>
            </div>
            <span className="text-3xl font-light text-zinc-900 dark:text-white">
              Mealie
            </span>
          </div>
        </div>

        {children}
      </div>
    </div>
  );
}
