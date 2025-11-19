#!/usr/bin/env python3
"""
Uptime Kuma Provisioning Script
Script untuk menambahkan monitor dan notification ke Uptime Kuma
"""

import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv
from uptime_kuma_api import UptimeKumaApi, MonitorType, NotificationType

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    url = os.getenv('UPTIME_KUMA_URL', 'http://localhost:3001')
    username = os.getenv('UPTIME_KUMA_USERNAME')
    password = os.getenv('UPTIME_KUMA_PASSWORD')
    teams_webhook = os.getenv('TEAMS_WEBHOOK')
    
    # Validate required environment variables
    if not username:
        print("Error: UPTIME_KUMA_USERNAME is not set in .env file")
        sys.exit(1)
    
    if not password:
        print("Error: UPTIME_KUMA_PASSWORD is not set in .env file")
        sys.exit(1)
    
    if not teams_webhook:
        print("Error: TEAMS_WEBHOOK is not set in .env file")
        sys.exit(1)
    
    # Read domains from domain.txt
    domain_file = os.path.join(os.path.dirname(__file__), 'domain.txt')
    if not os.path.exists(domain_file):
        print(f"Error: domain.txt not found at {domain_file}")
        sys.exit(1)
    
    # Parse domains from file
    monitor_urls = []
    with open(domain_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                monitor_urls.append(line)
    
    if not monitor_urls:
        print("Error: No URLs found in domain.txt")
        sys.exit(1)
    
    print(f"Found {len(monitor_urls)} URLs to monitor")
    
    try:
        print(f"Connecting to Uptime Kuma at {url}...")
        
        # Connect to Uptime Kuma
        api = UptimeKumaApi(url)
        
        # Login
        print(f"Logging in as {username}...")
        api.login(username, password)
        print("Login successful!")
        
        # Check if Teams notification already exists
        print("Checking for existing Teams notification...")
        existing_notifications = api.get_notifications()
        notification_id = None
        
        # Look for existing Teams notification with same webhook
        for notif in existing_notifications:
            if notif.get('type') == NotificationType.TEAMS:
                # Check both possible key names for webhook URL
                webhook = notif.get('webhookurl') or notif.get('webhookUrl')
                if webhook == teams_webhook:
                    notification_id = notif.get('id')
                    print(f"Found existing Teams notification with ID: {notification_id}")
                    break
        
        # Create new notification if not found
        if notification_id is None:
            print("Creating Teams notification channel...")
            notification_result = api.add_notification(
                name="Teams Webhook",
                type=NotificationType.TEAMS,
                webhookUrl=teams_webhook
            )
            print(f"Notification result: {notification_result}")
            
            # Try different possible keys for notification ID
            notification_id = (
                notification_result.get('notificationID') or 
                notification_result.get('id') or
                notification_result.get('notificationId')
            )
            
            # If still None, get from notifications list
            if notification_id is None:
                print("Fetching notification ID from notifications list...")
                notifications = api.get_notifications()
                for notif in notifications:
                    if notif.get('type') == NotificationType.TEAMS:
                        # Check both possible key names for webhook URL
                        webhook = notif.get('webhookurl') or notif.get('webhookUrl')
                        if webhook == teams_webhook:
                            notification_id = notif.get('id')
                            break
            
            if notification_id is None:
                raise Exception("Failed to get notification ID after creating notification")
            
            print(f"Teams notification created with ID: {notification_id}")
        
        # Validate notification_id before using
        if notification_id is None:
            raise Exception("Notification ID is None, cannot proceed with monitor creation")
        
        # Get existing monitors to avoid duplicates
        print("Checking existing monitors...")
        existing_monitors = api.get_monitors()
        existing_urls = {monitor.get('url') for monitor in existing_monitors}
        
        # Helper function to generate monitor name from URL
        def generate_monitor_name(url):
            parsed = urlparse(url)
            domain = parsed.netloc.replace('.qoin.id', '').replace('.qoinhub.id', '')
            # Convert domain to readable name
            name_parts = domain.split('-')
            name = ' '.join(word.capitalize() for word in name_parts)
            return f"{name} Health Check"
        
        # Add monitors for each URL
        created_count = 0
        skipped_count = 0
        
        for monitor_url in monitor_urls:
            # Skip if monitor already exists
            if monitor_url in existing_urls:
                print(f"⏭️  Skipping {monitor_url} (already exists)")
                skipped_count += 1
                continue
            
            monitor_name = generate_monitor_name(monitor_url)
            
            try:
                print(f"➕ Adding monitor for {monitor_url}...")
                monitor_result = api.add_monitor(
                    type=MonitorType.HTTP,
                    name=monitor_name,
                    url=monitor_url,
                    interval=60,
                    notificationIDList=[notification_id]
                )
                monitor_id = monitor_result.get('monitorId')
                print(f"   ✓ Monitor '{monitor_name}' created with ID: {monitor_id}")
                created_count += 1
            except Exception as e:
                print(f"   ✗ Failed to create monitor for {monitor_url}: {str(e)}")
                continue
        
        # Disconnect
        api.disconnect()
        print(f"\n{'='*60}")
        print(f"Provisioning completed!")
        print(f"  Created: {created_count} monitors")
        print(f"  Skipped: {skipped_count} monitors (already exist)")
        print(f"  Total:   {len(monitor_urls)} URLs processed")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

