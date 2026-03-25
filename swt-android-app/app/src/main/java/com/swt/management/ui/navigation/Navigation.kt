package com.swt.management.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PersonPin
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Assessment
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.swt.management.ui.screens.customer.CustomerScreen
import com.swt.management.ui.screens.driver.DriverScreen
import com.swt.management.ui.screens.home.HomeScreen
import com.swt.management.ui.screens.keyword.KeywordScreen
import com.swt.management.ui.screens.settings.SettingsScreen
import com.swt.management.ui.screens.stats.StatsScreen

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Home : Screen("home", "首頁", Icons.Default.Home)
    object Keyword : Screen("keyword", "關鍵字", Icons.Default.List)
    object Customer : Screen("customer", "客戶", Icons.Default.Person)
    object Driver : Screen("driver", "司機", Icons.Default.PersonPin)
    object Stats : Screen("stats", "統計", Icons.Default.Assessment)
    object Settings : Screen("settings", "設定", Icons.Default.Settings)
}

val bottomNavItems = listOf(
    Screen.Home,
    Screen.Keyword,
    Screen.Customer,
    Screen.Driver,
    Screen.Stats,
    Screen.Settings
)

@Composable
fun SWTNavHost() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                bottomNavItems.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.title) },
                        label = { Text(screen.title) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Home.route) { HomeScreen() }
            composable(Screen.Keyword.route) { KeywordScreen() }
            composable(Screen.Customer.route) { CustomerScreen() }
            composable(Screen.Driver.route) { DriverScreen() }
            composable(Screen.Stats.route) { StatsScreen() }
            composable(Screen.Settings.route) { SettingsScreen() }
        }
    }
}
