import React from "react"
import { NavLink } from "react-router-dom"
import { Settings, User, LogOut } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import "../assets/styles/Header.css"

const Header = () => {
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
  }

  return (
    <header className="dashboard-header">
      <div className="header-left">
        {/* Text-based Logo */}
        <div className="logo-container">
          <div className="text-blue-600 font-bold text-xl tracking-wide">
            MEDICHAIN
          </div>
        </div>

        <nav className="nav-links">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            DASHBOARD
          </NavLink>

          <NavLink 
            to="/patients" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            PATIENTS
          </NavLink>

          <NavLink 
            to="/ai-assistant" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            AI ASSISTANT
          </NavLink>

          <NavLink 
            to="/prescriptions" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            PRESCRIPTIONS
          </NavLink>
        </nav>
      </div>

      <div className="header-right">
        <button className="icon-button"><Settings size={24} /></button>
        <button className="icon-button"><User size={24} /></button>
        <button className="icon-button" onClick={handleLogout}><LogOut size={24} /></button>
      </div>
    </header>
  )
}

export default Header
