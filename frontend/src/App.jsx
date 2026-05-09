import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppProvider } from './contexts/AppContext'
import AppLayout from './components/AppLayout'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Home from './pages/Home'
import MealPlans from './pages/MealPlans'
import Workouts from './pages/Workouts'
import Friends from './pages/Friends'
import Challenges from './pages/Challenges'
import Profile from './pages/Profile'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />

          <Route
            element={
              <PrivateRoute>
                <AppLayout />
              </PrivateRoute>
            }
          >
            <Route path="/" element={<Home />} />
            <Route path="/mealplans" element={<MealPlans />} />
            <Route path="/workouts" element={<Workouts />} />
            <Route path="/friends" element={<Friends />} />
            <Route path="/challenges" element={<Challenges />} />
            <Route path="/u/:username" element={<Profile />} />
            <Route path="/main" element={<Navigate to="/" replace />} />
          </Route>

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  )
}
