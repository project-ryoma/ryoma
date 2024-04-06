import { Icons } from "@/components/icons";
import { NavItem, SidebarNavItem } from "@/types";

export type User = {
  id: number;
  name: string;
  company: string;
  role: string;
  verified: boolean;
  status: string;
};
export const users: User[] = [
  {
    id: 1,
    name: "Candice Schiner",
    company: "Dell",
    role: "Frontend Developer",
    verified: false,
    status: "Active",
  },
  {
    id: 2,
    name: "John Doe",
    company: "TechCorp",
    role: "Backend Developer",
    verified: true,
    status: "Active",
  },
  {
    id: 3,
    name: "Alice Johnson",
    company: "WebTech",
    role: "UI Designer",
    verified: true,
    status: "Active",
  },
  {
    id: 4,
    name: "David Smith",
    company: "Innovate Inc.",
    role: "Fullstack Developer",
    verified: false,
    status: "Inactive",
  },
  {
    id: 5,
    name: "Emma Wilson",
    company: "TechGuru",
    role: "Product Manager",
    verified: true,
    status: "Active",
  },
  {
    id: 6,
    name: "James Brown",
    company: "CodeGenius",
    role: "QA Engineer",
    verified: false,
    status: "Active",
  },
  {
    id: 7,
    name: "Laura White",
    company: "SoftWorks",
    role: "UX Designer",
    verified: true,
    status: "Active",
  },
  {
    id: 8,
    name: "Michael Lee",
    company: "DevCraft",
    role: "DevOps Engineer",
    verified: false,
    status: "Active",
  },
  {
    id: 9,
    name: "Olivia Green",
    company: "WebSolutions",
    role: "Frontend Developer",
    verified: true,
    status: "Active",
  },
  {
    id: 10,
    name: "Robert Taylor",
    company: "DataTech",
    role: "Data Analyst",
    verified: false,
    status: "Active",
  },
];

export const navItems: NavItem[] = [
  {
    title: "Chat",
    href: "/chat",
    icon: "chat",
    label: "chat",
  },
  {
    title: "Data Source",
    href: "/datasource",
    icon: "media",
    label: "datasource",
  },
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: "dashboard",
    label: "Dashboard",
  },
  {
    title: "User",
    href: "/user",
    icon: "user",
    label: "user",
  },
  {
    title: "Profile",
    href: "/profile",
    icon: "profile",
    label: "profile",
  },
];


export type DataSource = {
  id: number;
  name: string;
  description: string;
  label: string;
  status: string;
};

export const datasources: DataSource[] = [
  {
    id: 1,
    name: "Postgres",
    description: "Postgres database",
    label: "Postgres",
    status: "connected",
  },
  {
    id: 2,
    name: "MySQL",
    description: "MySQL database",
    label: "MySQL",
    status: "disconnected",
  },
  {
    id: 3,
    name: "MongoDB",
    description: "MongoDB database",
    label: "MongoDB",
    status: "connected",
  },
  {
    id: 4,
    name: "Redis",
    description: "Redis database",
    label: "Redis",
    status: "disconnected",
  },
  {
    id: 5,
    name: "Elasticsearch",
    description: "Elasticsearch database",
    label: "Elasticsearch",
    status: "connected",
  },
];