# JPetStore UI

Premium responsive React storefront for the JPetStore modernization program.

## Stack

React 18, Vite 6, TypeScript (strict), Tailwind CSS, Framer Motion, React Router, Axios, Zustand, React Hook Form, Zod, Lucide React.

## Development

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env` and adjust:

- `VITE_API_BASE_URL` — FastAPI base URL (no trailing slash)
- `VITE_USE_MOCK_API` — `true` uses fixtures for catalog/cart/orders; auth uses mock sign-on when `true`, or live `/api/v1/auth/*` when `false`

## Theme

Dark mode is the default. Toggle in header (desktop + mobile drawer). Preference stored in `localStorage` key `jpetstore-theme`.

Design tokens live under `src/styles/`. See `design-system/jpetstore-ui/MASTER.md` from UI UX Pro Max.

## Backend integration

Implemented against `../docs/API_SPECIFICATION.md`. With `VITE_USE_MOCK_API=false` and `VITE_API_BASE_URL` pointing at the FastAPI server, auth, catalog, cart (JWT), checkout, and orders use live `/api/v1/*` endpoints where the backend implements them. See `../docs/API_IMPLEMENTATION_STATUS.md` for gaps (e.g. guest cart).

Demo mock sign-on: `j2ee` / `j2ee`.
