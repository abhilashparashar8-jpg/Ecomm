import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import useStore from '../store/useStore';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState(null);
  
  const setUser = useStore((state) => state.setUser);
  const navigate = useNavigate();

  const handleAuth = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      if (isRegistering) {
        // Step 1: Register
        await api.post('/auth/register', { email, password, full_name: fullName });
      }
      
      // Step 2: Login via form data (OAuth2PasswordRequestForm expects URLSearchParams)
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);
      
      const res = await api.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const token = res.data.access_token;
      localStorage.setItem('token', token);
      setUser({ email });
      navigate('/');
      
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Authentication failed. Please try again.");
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-black">
      {/* Background Image Overlay */}
      <div 
        className="absolute inset-0 opacity-50 bg-cover bg-center pointer-events-none"
        style={{ backgroundImage: "url('/background.png')" }}
      />
      <div className="absolute inset-0 bg-black/40" />

      {/* Main Form Container */}
      <div className="relative z-10 w-full max-w-[450px] bg-black/75 p-16 rounded-md shadow-2xl backdrop-blur-sm mt-8 mb-24">
        <h1 className="text-3xl font-bold text-white mb-8">
          {isRegistering ? 'Sign Up' : 'Sign In'}
        </h1>
        
        {error && (
          <div className="bg-[#e87c03] text-white p-3 rounded mb-6 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleAuth} className="flex flex-col gap-4">
          {isRegistering && (
            <input 
              type="text" 
              placeholder="Full Name"
              value={fullName} 
              onChange={e => setFullName(e.target.value)}
              className="w-full bg-[#333] text-white rounded p-4 outline-none focus:bg-[#444] transition"
              required
            />
          )}
          <input 
            type="email" 
            placeholder="Email or phone number"
            value={email} 
            onChange={e => setEmail(e.target.value)}
            className="w-full bg-[#333] text-white rounded p-4 outline-none focus:bg-[#444] transition"
            required
          />

          <input 
            type="password" 
            placeholder="Password"
            value={password} 
            onChange={e => setPassword(e.target.value)}
            className="w-full bg-[#333] text-white rounded p-4 outline-none focus:bg-[#444] transition"
            required
            minLength={6}
          />

          <button type="submit" className="w-full bg-red-600 text-white font-bold rounded py-4 mt-6 hover:bg-red-700 transition duration-300">
            {isRegistering ? 'Create Account' : 'Sign In'}
          </button>

          {/* Demo Login Button for Localhost Demo - Only shown in DEV mode */}
          {import.meta.env.VITE_APP_MODE === 'dev' && (
            <button 
              type="button"
              onClick={() => {
                setUser({ email: 'puneet@example.com' });
                navigate('/');
              }}
              className="w-full bg-blue-600/30 text-blue-400 border border-blue-600 font-bold rounded py-2 mt-2 hover:bg-blue-600/50 transition duration-300 text-sm"
            >
              🚀 DEMO MODE: Skip Backend
            </button>
          )}
        </form>

        <div className="mt-4 flex justify-between text-[#b3b3b3] text-sm">
           <div className="flex items-center gap-1">
             <input type="checkbox" id="rememberMe" className="w-4 h-4 bg-[#737373]" />
             <label htmlFor="rememberMe">Remember me</label>
           </div>
           <a href="#" className="hover:underline">Need help?</a>
        </div>

        <div className="mt-16 text-[#737373] text-base">
           {isRegistering ? (
             <p>
               Already subscribed? <span className="text-white hover:underline cursor-pointer" onClick={() => setIsRegistering(false)}>Sign in now.</span>
             </p>
           ) : (
             <p>
               New to StreamShop? <span className="text-white hover:underline cursor-pointer" onClick={() => setIsRegistering(true)}>Sign up now.</span>
             </p>
           )}
           <p className="text-xs mt-4">
             This page is protected by Google reCAPTCHA to ensure you're not a bot. <a href="#" className="text-blue-600 hover:underline">Learn more.</a>
           </p>
        </div>
      </div>
    </div>
  );
}
