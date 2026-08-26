# Linux Essentials & Host Administration

## Common Administrative Commands

```bash
# Process and Resource Monitoring
top                  # Interactive process & resource viewer
ps aux | grep java   # Check running Java processes
free -h              # Display free and used memory in human-readable format
df -h                # Display disk space utilization

# Network & Ports
ip a                 # Display IP addresses on network interfaces
ss -tulpn            # Show listening TCP/UDP ports and associated processes
curl -I localhost:8080/health # Verify HTTP response

# Service Management
sudo systemctl status docker   # Check Docker daemon status
sudo systemctl restart k3s     # Restart k3s service
sudo journalctl -u k3s -f      # Follow live systemd logs for k3s
```

## Security Best Practices
- Non-root user permissions (`ubuntu` user with sudo and docker group membership).
- Application containers run as an unprivileged user (`devorbit: 1001`).
