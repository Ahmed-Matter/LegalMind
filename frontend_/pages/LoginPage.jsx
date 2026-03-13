import LoginForm from "../components/LoginForm";

export default function LoginPage({ onLogin }) {

  return (

    <div className="min-h-screen flex items-center justify-center bg-slate-900">

      <LoginForm onSuccess={onLogin} />

    </div>

  );

}