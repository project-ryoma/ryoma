import {
  AlertTriangle,
  ArrowRight,
  Check,
  ChevronLeft,
  ChevronRight,
  CircuitBoardIcon,
  Command,
  CreditCard,
  File,
  FileText,
  HelpCircle,
  Image,
  Laptop,
  LayoutDashboardIcon,
  Loader2,
  LogIn,
  LucideIcon,
  LucideProps,
  MessageCircle,
  Moon,
  MoreVertical,
  Pizza,
  Plus,
  Settings,
  SunMedium,
  Trash,
  Twitter,
  User,
  User2Icon,
  UserX2Icon,
  X,
} from "lucide-react";

export type Icon = LucideIcon;

export const Icons = {
  dashboard: LayoutDashboardIcon,
  logo: Command,
  login: LogIn,
  close: X,
  profile: User2Icon,
  spinner: Loader2,
  kanban: CircuitBoardIcon,
  chevronLeft: ChevronLeft,
  chevronRight: ChevronRight,
  trash: Trash,
  employee: UserX2Icon,
  post: FileText,
  page: File,
  media: Image,
  settings: Settings,
  billing: CreditCard,
  ellipsis: MoreVertical,
  add: Plus,
  warning: AlertTriangle,
  user: User,
  arrowRight: ArrowRight,
  help: HelpCircle,
  pizza: Pizza,
  sun: SunMedium,
  chat: MessageCircle,
  moon: Moon,
  laptop: Laptop,
  aita: ({ ...props }: LucideProps) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      zoomAndPan="magnify"
      viewBox="0 0 810 809.999993"
      preserveAspectRatio="xMidYMid meet"
      version="1.0"
      {...props}
    ><defs><g/></defs><g fill="#000000" fill-opacity="1"><g transform="translate(124.682004, 536.316511)"><g><path d="M 8.15625 0 L 85.8125 -230.5 L 117.375 -230.5 L 193.609375 0 L 165.609375 0 L 141.484375 -70.921875 L 51.0625 -70.921875 L 26.953125 0 Z M 56.03125 -85.453125 L 136.875 -85.453125 L 96.8125 -209.921875 Z M 56.03125 -85.453125 "/></g></g></g><g fill="#000000" fill-opacity="1"><g transform="translate(319.006544, 536.316511)"><g><path d="M 39.359375 -213.125 C 35.109375 -213.125 31.679688 -214.421875 29.078125 -217.015625 C 26.003906 -220.085938 24.46875 -223.875 24.46875 -228.375 C 24.46875 -232.863281 26.003906 -236.644531 29.078125 -239.71875 C 31.679688 -242.3125 35.109375 -243.609375 39.359375 -243.609375 C 43.847656 -243.609375 47.394531 -242.429688 50 -240.078125 C 52.832031 -236.992188 54.25 -233.09375 54.25 -228.375 C 54.25 -224.113281 52.832031 -220.328125 50 -217.015625 C 46.6875 -214.421875 43.140625 -213.125 39.359375 -213.125 Z M 26.234375 0 L 26.234375 -177.3125 L 52.125 -177.3125 L 52.125 0 Z M 26.234375 0 "/></g></g></g><g fill="#000000" fill-opacity="1"><g transform="translate(390.637079, 536.316511)"><g><path d="M 70.21875 3.546875 C 57.445312 3.546875 47.988281 -0.410156 41.84375 -8.328125 C 35.695312 -16.253906 32.625 -29.316406 32.625 -47.515625 L 32.625 -159.921875 L 14.1875 -159.921875 L 14.1875 -174.828125 L 32.625 -176.953125 L 42.203125 -233.328125 L 58.515625 -233.328125 L 58.515625 -177.3125 L 103.90625 -177.3125 L 103.90625 -159.921875 L 58.515625 -159.921875 L 58.515625 -53.90625 C 58.515625 -38.53125 59.988281 -27.945312 62.9375 -22.15625 C 65.894531 -16.363281 71.039062 -13.46875 78.375 -13.46875 C 84.28125 -13.46875 89.597656 -14.054688 94.328125 -15.234375 C 99.054688 -16.421875 101.421875 -17.132812 101.421875 -17.375 L 103.1875 -3.1875 C 102.71875 -2.71875 101.238281 -1.953125 98.75 -0.890625 C 96.269531 0.171875 92.609375 1.175781 87.765625 2.125 C 82.921875 3.070312 77.070312 3.546875 70.21875 3.546875 Z M 70.21875 3.546875 "/></g></g></g><g fill="#000000" fill-opacity="1"><g transform="translate(499.146747, 536.316511)"><g><path d="M 63.125 3.546875 C 47.519531 3.546875 34.988281 -0.289062 25.53125 -7.96875 C 16.070312 -15.65625 11.34375 -26.359375 11.34375 -40.078125 C 11.34375 -74.828125 44.796875 -95.75 111.703125 -102.84375 L 111.703125 -121.625 C 111.703125 -138.414062 108.984375 -149.882812 103.546875 -156.03125 C 98.109375 -162.175781 88.535156 -165.25 74.828125 -165.25 C 68.679688 -165.25 62.414062 -164.125 56.03125 -161.875 C 49.644531 -159.632812 44.265625 -157.269531 39.890625 -154.78125 C 35.515625 -152.300781 32.738281 -150.707031 31.5625 -150 L 28.71875 -164.53125 C 29.90625 -165.476562 32.921875 -167.253906 37.765625 -169.859375 C 42.609375 -172.460938 48.753906 -174.941406 56.203125 -177.296875 C 63.648438 -179.660156 71.15625 -180.84375 78.71875 -180.84375 C 99.050781 -180.84375 113.945312 -176.585938 123.40625 -168.078125 C 132.863281 -159.566406 137.59375 -144.554688 137.59375 -123.046875 L 137.59375 -36.171875 C 137.59375 -26.710938 138.476562 -20.328125 140.25 -17.015625 C 142.019531 -13.710938 144.207031 -12.0625 146.8125 -12.0625 C 148.9375 -12.0625 151.535156 -12.472656 154.609375 -13.296875 C 157.679688 -14.117188 159.691406 -14.769531 160.640625 -15.25 L 161.703125 -3.1875 C 159.804688 -2.476562 155.785156 -1.179688 149.640625 0.703125 C 143.492188 2.597656 138.296875 3.546875 134.046875 3.546875 C 127.898438 3.546875 123.171875 1.597656 119.859375 -2.296875 C 116.546875 -6.203125 114.535156 -13.117188 113.828125 -23.046875 L 113.46875 -23.046875 C 113.46875 -22.097656 111.578125 -19.378906 107.796875 -14.890625 C 104.015625 -10.398438 98.398438 -6.203125 90.953125 -2.296875 C 83.503906 1.597656 74.226562 3.546875 63.125 3.546875 Z M 70.921875 -12.0625 C 79.429688 -12.0625 86.757812 -13.953125 92.90625 -17.734375 C 99.050781 -21.515625 103.71875 -25.648438 106.90625 -30.140625 C 110.101562 -34.628906 111.703125 -37.226562 111.703125 -37.9375 L 111.703125 -89.71875 C 90.191406 -87.351562 72.519531 -82.742188 58.6875 -75.890625 C 44.851562 -69.035156 37.9375 -58.160156 37.9375 -43.265625 C 37.9375 -33.097656 40.890625 -25.351562 46.796875 -20.03125 C 52.710938 -14.71875 60.753906 -12.0625 70.921875 -12.0625 Z M 70.921875 -12.0625 "/></g></g></g>
    </svg>
  ),
  gitHub: ({ ...props }: LucideProps) => (
    <svg
      aria-hidden="true"
      focusable="false"
      data-prefix="fab"
      data-icon="github"
      role="img"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 496 512"
      {...props}
    >
      <path
        fill="currentColor"
        d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3 .3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5 .3-6.2 2.3zm44.2-1.7c-2.9 .7-4.9 2.6-4.6 4.9 .3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3 .7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3 .3 2.9 2.3 3.9 1.6 1 3.6 .7 4.3-.7 .7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3 .7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3 .7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"
      ></path>
    </svg>
  ),
  twitter: Twitter,
  check: Check,
  completeMode: ({ ...props }: LucideProps) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="none"
      {...props}
    >
      <rect x="4" y="3" width="12" height="2" rx="1" fill="currentColor"></rect>
      <rect x="4" y="7" width="12" height="2" rx="1" fill="currentColor"></rect>
      <rect x="4" y="11" width="3" height="2" rx="1" fill="currentColor"></rect>
      <rect x="4" y="15" width="3" height="2" rx="1" fill="currentColor"></rect>
      <rect
        x="8.5"
        y="11"
        width="3"
        height="2"
        rx="1"
        fill="currentColor"
      ></rect>
      <rect
        x="8.5"
        y="15"
        width="3"
        height="2"
        rx="1"
        fill="currentColor"
      ></rect>
      <rect
        x="13"
        y="11"
        width="3"
        height="2"
        rx="1"
        fill="currentColor"
      ></rect>
    </svg>
  ),
  insertMode: ({ ...props }: LucideProps) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="none"
      {...props}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M14.491 7.769a.888.888 0 0 1 .287.648.888.888 0 0 1-.287.648l-3.916 3.667a1.013 1.013 0 0 1-.692.268c-.26 0-.509-.097-.692-.268L5.275 9.065A.886.886 0 0 1 5 8.42a.889.889 0 0 1 .287-.64c.181-.17.427-.267.683-.269.257-.002.504.09.69.258L8.903 9.87V3.917c0-.243.103-.477.287-.649.183-.171.432-.268.692-.268.26 0 .509.097.692.268a.888.888 0 0 1 .287.649V9.87l2.245-2.102c.183-.172.432-.269.692-.269.26 0 .508.097.692.269Z"
        fill="currentColor"
      ></path>
      <rect x="4" y="15" width="3" height="2" rx="1" fill="currentColor"></rect>
      <rect
        x="8.5"
        y="15"
        width="3"
        height="2"
        rx="1"
        fill="currentColor"
      ></rect>
      <rect
        x="13"
        y="15"
        width="3"
        height="2"
        rx="1"
        fill="currentColor"
      ></rect>
    </svg>
  ),
  editMode: ({ ...props }: LucideProps) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="none"
      {...props}
    >
      <rect x="4" y="3" width="12" height="2" rx="1" fill="currentColor"></rect>
      <rect x="4" y="7" width="12" height="2" rx="1" fill="currentColor"></rect>
      <rect x="4" y="11" width="3" height="2" rx="1" fill="currentColor"></rect>
      <rect x="4" y="15" width="4" height="2" rx="1" fill="currentColor"></rect>
      <rect
        x="8.5"
        y="11"
        width="3"
        height="2"
        rx="1"
        fill="currentColor"
      ></rect>
      <path
        d="M17.154 11.346a1.182 1.182 0 0 0-1.671 0L11 15.829V17.5h1.671l4.483-4.483a1.182 1.182 0 0 0 0-1.671Z"
        fill="currentColor"
      ></path>
    </svg>
  )
};
