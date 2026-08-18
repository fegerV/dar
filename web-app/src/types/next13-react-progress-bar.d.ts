declare module 'next13-react-progress-bar' {
  import { ReactNode } from 'react'

  interface ProgressBarProps {
    height?: string | number
    color?: string
    options?: {
      showSpinner?: boolean
      delay?: number
    }
  }

  const ProgressBar: (props: ProgressBarProps) => ReactNode
  export { ProgressBar }
  export default ProgressBar
}
