import type { InputHTMLAttributes } from 'react'
type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> & { onCheckedChange: (checked: boolean) => void }
export function Checkbox({ onCheckedChange, ...props }: Props) {
  return <input type="checkbox" {...props} onChange={e => onCheckedChange(e.target.checked)} />
}
