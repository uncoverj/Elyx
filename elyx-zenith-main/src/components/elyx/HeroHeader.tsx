import { motion } from "framer-motion";
import { Shield, ThumbsUp, ThumbsDown, Send, Sparkles } from "lucide-react";
import heroBanner from "@/assets/hero-banner.jpg";
import { BackendProfile } from "@/lib/api";

interface HeroHeaderProps {
  profile: BackendProfile;
}

export function HeroHeader({ profile }: HeroHeaderProps) {
  const trustPercent = profile.trust_score <= 1 ? profile.trust_score * 100 : profile.trust_score;
  const telegramHandle = profile.username ? `@${profile.username}` : `id:${profile.tg_id}`;

  const parsedTag = (() => {
    const riot = profile.tags?.find((x) => x.includes("#"));
    if (riot && riot.includes("#")) return riot.split("#").slice(1).join("#");
    return profile.game_name === "Valorant" ? "VAL" : "ELYX";
  })();

  return (
    <div className="relative overflow-hidden">
      {/* Banner with overlay */}
      <div className="h-36 md:h-52 lg:h-64 relative">
        <img src={heroBanner} alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-b from-background/10 via-background/30 to-background" />
        <div className="absolute inset-0 bg-gradient-to-r from-background/40 to-transparent" />
        
        {/* Watermark */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="absolute top-4 right-4 font-display text-5xl md:text-6xl lg:text-7xl font-bold text-foreground/[0.04] tracking-[-0.05em] leading-[0.85] select-none"
        >
          VALO<br />RANT
        </motion.div>

        {/* ELYX logo top-left on mobile */}
        <div className="absolute top-3 left-4 lg:hidden">
          <span className="font-display text-lg font-bold gradient-text tracking-wider">ELYX</span>
        </div>
      </div>

      {/* Profile card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="relative px-4 md:px-6 -mt-12 md:-mt-14"
      >
        <div className="flex items-end gap-3.5 md:gap-5">
          {/* Avatar */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 300 }}
            className="relative"
          >
            <div className="w-[72px] h-[72px] md:w-[88px] md:h-[88px] rounded-2xl glass-card-static flex items-center justify-center shrink-0 glow-red relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/10" />
              <Shield size={36} className="text-primary relative z-10" />
            </div>
            {/* Online indicator */}
            <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-success border-[3px] border-background" />
          </motion.div>

          <div className="flex-1 min-w-0 pb-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl md:text-2xl lg:text-3xl font-display font-bold truncate tracking-tight">
                {profile.nickname}
              </h1>
              <span className="text-xs text-muted-foreground font-mono bg-secondary/60 px-1.5 py-0.5 rounded">
                #{parsedTag}
              </span>
              {profile.is_premium ? (
                <div className="flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20">
                  <Sparkles size={10} className="text-primary" />
                  <span className="text-[10px] font-bold text-primary">PRO</span>
                </div>
              ) : null}
            </div>
            
            <div className="flex items-center gap-3 mt-1.5 flex-wrap">
              {/* Telegram badge */}
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-info/10 border border-info/20">
                <Send size={10} className="text-info" />
                <span className="text-[11px] text-info font-medium">{telegramHandle}</span>
              </div>
              
              {/* Trust */}
              <div className="flex items-center gap-1 text-xs">
                <Shield size={12} className="text-primary" />
                <span className="text-foreground font-bold">{trustPercent.toFixed(1)}%</span>
              </div>
              
              {/* Likes/dislikes */}
              <div className="flex items-center gap-2.5 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <ThumbsUp size={11} className="text-success" />
                  <span className="font-medium">{profile.trust_up}</span>
                </span>
                <span className="flex items-center gap-1">
                  <ThumbsDown size={11} className="text-destructive" />
                  <span className="font-medium">{profile.trust_down}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
