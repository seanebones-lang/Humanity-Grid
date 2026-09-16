import * as React from 'react'
import { cn } from '@/lib/utils'

export interface SliderProps extends React.ComponentPropsWithoutRef<typeof React.ForwardRefExoticComponent<React.SliderHTMLAttributes<HTMLInputElement>>> {
  value: number[]
  onValueChange: (value: number[]) => void
  max?: number
  min?: number
  step?: number
  disabled?: boolean
  className?: string
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, value, onValueChange, max = 100, min = 0, step = 1, disabled, ...props }, ref) => {
    return (
      <div className="relative w-full" data-disabled={disabled}>
        <input
          type="range"
          ref={ref}
          className={cn(
            'appearance-none w-full h-2 bg-surface rounded-full cursor-pointer',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            className
          )}
          min={min}
          max={max}
          step={step}
          value={value[0]}
          onChange={(e) => onValueChange([Number(e.target.value)])}
          disabled={disabled}
          {...props}
        />
        <div
          className="absolute h-full bg-primary rounded-full pointer-events-none"
          style={{
            left: '0%',
            width: `${((value[0] - min) / (max - min)) * 100}%`,
          }}
        />
      </div>
    )
  }
)
Slider.displayName = 'Slider'

export { Slider }