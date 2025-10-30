import { lazy } from "react";
import { Navigate } from "react-router-dom";
import type { RouteObject } from "react-router-dom";

import { AppLayout } from "@/layouts/AppLayout";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

const DashboardPage = lazy(() =>
  import("@/pages/DashboardPage").then((module) => ({ default: module.DashboardPage })),
);
const PartnersPage = lazy(() =>
  import("@/pages/PartnersPage").then((module) => ({ default: module.PartnersPage })),
);
const StoresPage = lazy(() =>
  import("@/pages/StoresPage").then((module) => ({ default: module.StoresPage })),
);
const ReceiptsPage = lazy(() =>
  import("@/pages/ReceiptsPage").then((module) => ({ default: module.ReceiptsPage })),
);
const ReportsPage = lazy(() =>
  import("@/pages/ReportsPage").then((module) => ({ default: module.ReportsPage })),
);
const UsersPage = lazy(() =>
  import("@/pages/UsersPage").then((module) => ({ default: module.UsersPage })),
);
const AccountPage = lazy(() =>
  import("@/pages/AccountPage").then((module) => ({ default: module.AccountPage })),
);
const ConnectPage = lazy(() =>
  import("@/pages/ConnectPage").then((module) => ({ default: module.ConnectPage })),
);
const LoginPage = lazy(() =>
  import("@/pages/LoginPage").then((module) => ({ default: module.LoginPage })),
);

export type NavigationSection = "primary" | "user";

export type RouteMeta = {
  /** Caminho absoluto que identifica a rota. */
  fullPath: string;
  /** Identifica se a rota exige autenticação. */
  requiresAuth?: boolean;
  /** Rótulo utilizado em breadcrumbs. */
  breadcrumb?: string;
  /** Configuração de uso em menus de navegação. */
  navigation?: {
    section: NavigationSection;
    label: string;
    requiresAuth?: boolean;
    order?: number;
  };
};

export type AppRouteObject = RouteObject & {
  meta?: RouteMeta;
  children?: AppRouteObject[];
};

export const appRoutes: AppRouteObject[] = [
  {
    path: "/login",
    element: <LoginPage />,
    meta: {
      fullPath: "/login",
      breadcrumb: "Entrar",
      requiresAuth: false,
    },
  },
  {
    element: <AppLayout />,
    children: [
      {
        path: "/conectar",
        element: <ConnectPage />,
        meta: {
          fullPath: "/conectar",
          breadcrumb: "Conectar",
          requiresAuth: false,
          navigation: {
            section: "primary",
            label: "Conectar",
            requiresAuth: false,
            order: 4,
          },
        },
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            index: true,
            element: <DashboardPage />,
            meta: {
              fullPath: "/",
              breadcrumb: "Início",
              requiresAuth: true,
              navigation: {
                section: "primary",
                label: "Início",
                requiresAuth: true,
                order: 1,
              },
            },
          },
          {
            path: "/parceiros",
            element: <PartnersPage />,
            meta: {
              fullPath: "/parceiros",
              breadcrumb: "Parceiros",
              requiresAuth: true,
              navigation: {
                section: "primary",
                label: "Parceiros",
                requiresAuth: true,
                order: 2,
              },
            },
          },
          {
            path: "/lojas",
            element: <StoresPage />,
            meta: {
              fullPath: "/lojas",
              breadcrumb: "Lojas",
              requiresAuth: true,
              navigation: {
                section: "primary",
                label: "Lojas",
                requiresAuth: true,
                order: 3,
              },
            },
          },
          {
            path: "/comprovantes",
            element: <ReceiptsPage />,
            meta: {
              fullPath: "/comprovantes",
              breadcrumb: "Comprovantes",
              requiresAuth: true,
              navigation: {
                section: "primary",
                label: "Comprovantes",
                requiresAuth: true,
                order: 5,
              },
            },
          },
          {
            path: "/relatorios",
            element: <ReportsPage />,
            meta: {
              fullPath: "/relatorios",
              breadcrumb: "Relatórios",
              requiresAuth: true,
              navigation: {
                section: "primary",
                label: "Relatórios",
                requiresAuth: true,
                order: 6,
              },
            },
          },
          {
            path: "/usuarios",
            element: <UsersPage />,
            meta: {
              fullPath: "/usuarios",
              breadcrumb: "Usuários",
              requiresAuth: true,
              navigation: {
                section: "user",
                label: "Usuários",
                requiresAuth: true,
                order: 1,
              },
            },
          },
          {
            path: "/account",
            element: <AccountPage />,
            meta: {
              fullPath: "/account",
              breadcrumb: "Minha Conta",
              requiresAuth: true,
              navigation: {
                section: "user",
                label: "Minha Conta",
                requiresAuth: true,
                order: 2,
              },
            },
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
];

type RouteAccumulator = RouteMeta[];

const collectRouteMeta = (routes: AppRouteObject[], acc: RouteAccumulator = []) => {
  routes.forEach((route) => {
    if (route.meta?.fullPath) {
      acc.push(route.meta);
    }

    if (route.children) {
      collectRouteMeta(route.children, acc);
    }
  });

  return acc;
};

export const resolvedRouteMeta = collectRouteMeta(appRoutes);

const hasNavigation = (
  route: RouteMeta,
): route is RouteMeta & { navigation: NonNullable<RouteMeta["navigation"]> } =>
  Boolean(route.navigation);

export const navigationRoutes = resolvedRouteMeta.filter(hasNavigation);

export type NavigationLink = {
  to: string;
  label: string;
  requiresAuth: boolean;
  section: NavigationSection;
  order: number;
};

const toNavigationLink = (route: typeof navigationRoutes[number]): NavigationLink => ({
  to: route.fullPath,
  label: route.navigation.label,
  requiresAuth: route.navigation.requiresAuth ?? route.requiresAuth ?? false,
  section: route.navigation.section,
  order: route.navigation.order ?? Number.MAX_SAFE_INTEGER,
});

const sortNavigationLinks = (links: NavigationLink[]) =>
  [...links].sort((first, second) => first.order - second.order);

export const navigationLinks = sortNavigationLinks(navigationRoutes.map(toNavigationLink));

export const primaryNavigationLinks = sortNavigationLinks(
  navigationLinks.filter((link) => link.section === "primary"),
);

export const userNavigationLinks = sortNavigationLinks(
  navigationLinks.filter((link) => link.section === "user"),
);

export const breadcrumbMap = resolvedRouteMeta.reduce<Record<string, string>>((map, route) => {
  if (route.breadcrumb) {
    map[route.fullPath] = route.breadcrumb;
  }
  return map;
}, {});
