import LoginForm from "../components/LoginForm";

export default function LoginPage({ onLogin }){

  return(

    <div className="flex items-center justify-center min-h-screen bg-slate-900">

      <LoginForm onLogin={onLogin}/>

    </div>

  );

}
