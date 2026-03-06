import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNav } from "@/components/elyx/BottomNav";
import { DesktopNav } from "@/components/elyx/DesktopNav";
import { ElyxProvider } from "@/context/ElyxContext";
import ProfilePage from "./pages/ProfilePage";
import StatsPage from "./pages/StatsPage";
import LeaderboardPage from "./pages/LeaderboardPage";
import MatchesPage from "./pages/MatchesPage";
import SettingsPage from "./pages/SettingsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ElyxProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <DesktopNav />
          <Routes>
            <Route path="/" element={<ProfilePage />} />
            <Route path="/stats" element={<StatsPage />} />
            <Route path="/leaderboard" element={<LeaderboardPage />} />
            <Route path="/matches" element={<MatchesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <BottomNav />
        </BrowserRouter>
      </TooltipProvider>
    </ElyxProvider>
  </QueryClientProvider>
);

export default App;
