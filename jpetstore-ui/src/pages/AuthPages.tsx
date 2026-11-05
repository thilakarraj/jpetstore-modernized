import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuthStore } from "@/store/authStore";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

export function SignOnPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((s) => s.login);
  const error = useAuthStore((s) => s.error);
  const isLoading = useAuthStore((s) => s.isLoading);
  const from = (location.state as { from?: string } | null)?.from ?? "/account";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "j2ee", password: "j2ee" },
  });

  const onSubmit = handleSubmit(async (values) => {
    try {
      await login(values);
      navigate(from, { replace: true });
    } catch {
      /* store holds error */
    }
  });

  return (
    <div className="mx-auto flex max-w-md flex-col px-4 py-14 sm:px-6">
      <h1 className="font-display text-4xl">Sign on</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Use your JPetStore username and password. Demo: <code>j2ee</code> / <code>j2ee</code>.
      </p>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Input label="Username" error={errors.username?.message} {...register("username")} />
        <Input
          label="Password"
          type="password"
          error={errors.password?.message}
          {...register("password")}
        />
        {error ? (
          <p className="text-sm text-error" role="alert">
            {error}
          </p>
        ) : null}
        <Button type="submit" className="w-full" loading={isLoading}>
          Sign on
        </Button>
      </form>
      <p className="mt-6 text-sm text-muted-foreground">
        Need an account?{" "}
        <Link to="/register" className="text-accent hover:underline">
          Register
        </Link>
      </p>
    </div>
  );
}

const registerSchema = z.object({
  username: z.string().min(3),
  password: z.string().min(4),
  email: z.string().email(),
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  address1: z.string().min(1),
  city: z.string().min(1),
  state: z.string().min(1),
  zip: z.string().min(1),
  country: z.string().min(1),
  phone: z.string().min(1),
  language_preference: z.enum(["english", "japanese"]),
  favourite_category_id: z.enum(["FISH", "DOGS", "REPTILES", "CATS", "BIRDS"]),
  list_option: z.boolean(),
  banner_option: z.boolean(),
});

type RegisterForm = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const registerUser = useAuthStore((s) => s.register);
  const error = useAuthStore((s) => s.error);
  const isLoading = useAuthStore((s) => s.isLoading);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      language_preference: "english",
      favourite_category_id: "DOGS",
      list_option: true,
      banner_option: true,
      country: "USA",
    },
  });

  const onSubmit = handleSubmit(async (values) => {
    try {
      await registerUser(values);
      navigate("/signon", { state: { registered: true } });
    } catch {
      /* handled in store */
    }
  });

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-4xl">Register</h1>
      <p className="mt-2 text-muted-foreground">
        Creates account, profile, and signon records — then return to sign on (no automatic JWT).
      </p>
      <form onSubmit={onSubmit} className="mt-8 grid gap-4 sm:grid-cols-2">
        <Input label="Username" error={errors.username?.message} {...register("username")} />
        <Input
          label="Password"
          type="password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Input label="Email" error={errors.email?.message} {...register("email")} className="sm:col-span-2" />
        <Input label="First name" error={errors.first_name?.message} {...register("first_name")} />
        <Input label="Last name" error={errors.last_name?.message} {...register("last_name")} />
        <Input label="Address" error={errors.address1?.message} {...register("address1")} className="sm:col-span-2" />
        <Input label="City" error={errors.city?.message} {...register("city")} />
        <Input label="State" error={errors.state?.message} {...register("state")} />
        <Input label="Zip" error={errors.zip?.message} {...register("zip")} />
        <Input label="Country" error={errors.country?.message} {...register("country")} />
        <Input label="Phone" error={errors.phone?.message} {...register("phone")} />
        <div className="sm:col-span-2">
          <label className="text-sm font-medium">Favourite category</label>
          <select
            className="mt-1.5 h-11 w-full rounded-lg border border-input-border bg-input px-3"
            {...register("favourite_category_id")}
          >
            <option value="FISH">Fish</option>
            <option value="DOGS">Dogs</option>
            <option value="REPTILES">Reptiles</option>
            <option value="CATS">Cats</option>
            <option value="BIRDS">Birds</option>
          </select>
        </div>
        <label className="flex cursor-pointer items-center gap-2 text-sm sm:col-span-2">
          <input type="checkbox" {...register("list_option")} />
          Enable My List
        </label>
        <label className="flex cursor-pointer items-center gap-2 text-sm sm:col-span-2">
          <input type="checkbox" {...register("banner_option")} />
          Enable category banner
        </label>
        {error ? <p className="text-sm text-error sm:col-span-2">{error}</p> : null}
        <Button type="submit" className="sm:col-span-2" loading={isLoading}>
          Register
        </Button>
      </form>
    </div>
  );
}

export function AccountPage() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  if (!user) {
    return <p className="p-10 text-muted-foreground">Loading profile…</p>;
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl">My account</h1>
          <p className="mt-2 text-muted-foreground">Signed in as {user.username}</p>
        </div>
        <Button variant="outline" onClick={logout}>
          Sign out
        </Button>
      </div>
      <dl className="mt-8 grid gap-4 rounded-xl border border-border bg-surface p-6 sm:grid-cols-2">
        <Field label="Email" value={user.email} />
        <Field label="Phone" value={user.phone} />
        <Field label="Name" value={`${user.first_name} ${user.last_name}`} />
        <Field label="Language" value={user.language_preference} />
        <Field label="Favourite category" value={user.favourite_category_id} />
        <Field label="Banner" value={user.banner_name ?? "—"} />
        <Field label="Address" value={`${user.address1}, ${user.city}, ${user.state} ${user.zip}`} className="sm:col-span-2" />
      </dl>
      <Link to="/orders" className="mt-6 inline-block text-accent hover:underline">
        View order history
      </Link>
    </div>
  );
}

function Field({
  label,
  value,
  className,
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className={className}>
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  );
}
