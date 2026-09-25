import React, { useEffect } from 'react';
import { Check, FileText } from 'lucide-react';

/**
 * Full-screen modal shown while a screening request is in flight.
 * Colors come entirely from theme tokens, so it follows light/dark mode.
 */
export default function EvaluationLoader({ open, title, subtitle, steps, activeStep }) {
  // Lock page scroll while the overlay is visible
  useEffect(() => {
    if (!open) return undefined;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, [open]);

  if (!open) return null;

  return (
    <div className="eval-loader-backdrop" role="presentation">
      <div
        className="eval-loader-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="eval-loader-title"
        aria-busy="true"
      >
        <div className="eval-loader-visual" aria-hidden="true">
          <span className="eval-loader-ring eval-loader-ring-outer" />
          <span className="eval-loader-ring eval-loader-ring-inner" />
          <span className="eval-loader-orbit">
            <span className="eval-loader-orbit-dot" />
          </span>
          <div className="eval-loader-doc">
            <FileText size={30} strokeWidth={1.6} />
            <span className="eval-loader-scanline" />
          </div>
        </div>

        <h2 id="eval-loader-title" className="eval-loader-title">{title}</h2>
        {subtitle && <p className="eval-loader-subtitle">{subtitle}</p>}

        <ol className="eval-loader-steps" aria-live="polite">
          {steps.map((step, i) => {
            const state = i < activeStep ? 'done' : i === activeStep ? 'active' : 'pending';
            return (
              <li key={step} className={`eval-loader-step eval-loader-step-${state}`}>
                <span className="eval-loader-step-marker">
                  {state === 'done' ? <Check size={12} strokeWidth={3} /> : <span className="eval-loader-step-dot" />}
                </span>
                <span className="eval-loader-step-label">{step}</span>
              </li>
            );
          })}
        </ol>

        <div className="eval-loader-progress" aria-hidden="true">
          <span className="eval-loader-progress-bar" />
        </div>
      </div>
    </div>
  );
}
