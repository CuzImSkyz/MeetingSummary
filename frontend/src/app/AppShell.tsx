
import { History, House, Settings } from 'lucide-react'
import type { ReactNode } from "react";
import styles from './AppShell.module.css'

const navigationItems = [
    { label: 'Home', icon: House, active: true},
    { label: 'Vergangene Meetings', icon: History, active: false},
]

type AppShellProps = {
    children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
    return (
        <div className={styles.shell}>
            <aside className={styles.sidebar}>
                <div className={styles.brand}>
                    <span className={styles.brandMark} aria-hidden="true">
                        M
                    </span>
                    <span>MeetMe</span>
                </div>

                <nav className={styles.navigation} aria-label='Hauptnavigation'>
                    {navigationItems.map(({ label, icon: Icon, active }) => (
                        <button 
                            className={`${styles.navButton} ${
                                active ? styles.navButtonActive : ''
                            }`}
                            type="button"
                            aria-current={active ? 'page' : undefined}
                            key={label}
                        >
                            <Icon aria-hidden="true" size={20} strokeWidth={1.8} />
                            <span>{label}</span>
                        </button>
                    ))}
                </nav>

                <button className={styles.navButton} type="button">
                    <Settings aria-hidden="true" size={20} strokeWidth={1.8} />
                    <span>Einstellungen</span>
                </button>
            </aside>

            <main className={styles.content}>{children}</main>
        </div>
    )
}
