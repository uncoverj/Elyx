import { ReactNode } from "react";

interface PageShellProps {
  children: ReactNode;
  className?: string;
}

export function PageShell({ children, className = "" }: PageShellProps) {
  return (
    <div className={`min-h-screen pb-28 lg:pb-8 lg:pt-20 ${className}`}>
      {children}
    </div>
  );
}

interface SectionTitleProps {
  icon?: ReactNode;
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function SectionTitle({ icon, title, subtitle, action }: SectionTitleProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {icon}
        <div>
          <h2 className="font-display font-bold text-base md:text-lg tracking-tight">{title}</h2>
          {subtitle && <p className="text-[11px] text-muted-foreground">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}
