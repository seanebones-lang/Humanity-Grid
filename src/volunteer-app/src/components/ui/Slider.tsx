import * as React from 'react'
import { cn } from '@/lib/utils'

export interface SliderProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'value' | 'onChange'> {
  value: number[]
  onValueChange: (value: number[]) => void
  max?: number
  min?: number
  step?: number
  disabled?: boolean
  className?: string
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, value, onValueChange, max = 100, min = 0, step = 1, disabled, style, ...props }, ref) => {
    const progress = max > min ? Math.max(0, Math.min(100, ((value[0] - min) / (max - min)) * 100)) : 0
    return (
      <input
        type="range"
        ref={ref}
        className={cn(
          'preview-slider w-full cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          className
        )}
        min={min}
        max={max}
        step={step}
        value={value[0]}
        style={{
          backgroundImage: `linear-gradient(to right, var(--color-primary) ${progress}%, var(--color-border) ${progress}%)`,
          ...style,
        }}
        onChange={(e) => onValueChange([Number(e.target.value)])}
        disabled={disabled}
        {...props}
      />
    )
  }
)
Slider.displayName = 'Slider'

export { Slider }
