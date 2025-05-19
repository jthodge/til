#!/bin/bash
# Deployment script for TIL deduplication migration

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-staging}
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 1
    fi
}

# Check environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    echo "Usage: $0 [staging|production]"
    exit 1
fi

log_info "Starting deployment to $ENVIRONMENT"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Step 1: Pre-deployment checks
log_info "Running pre-deployment checks..."

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    log_warning "You have uncommitted changes"
    confirm "Continue anyway?"
fi

# Run tests
log_info "Running tests..."
if ! uv run pytest tests/ -q; then
    log_error "Tests failed"
    exit 1
fi
log_info "Tests passed"

# Step 2: Environment-specific deployment
if [[ "$ENVIRONMENT" == "production" ]]; then
    log_warning "Deploying to PRODUCTION"
    confirm "Are you sure you want to deploy to production?"
    
    # Production deployment steps
    log_info "Backing up production database..."
    
    # Example for Heroku
    # heroku pg:backups:capture --app your-app-name
    # heroku pg:backups:download --app your-app-name --output "$BACKUP_DIR/til-prod-$TIMESTAMP.db"
    
    # Example for direct server
    # ssh production-server "cp /path/to/til.db /path/to/til.db.backup-$TIMESTAMP"
    # scp production-server:/path/to/til.db "$BACKUP_DIR/til-prod-$TIMESTAMP.db"
    
    log_info "Running migration on production..."
    # Add your production migration command here
    
else
    # Staging deployment
    log_info "Deploying to staging..."
    
    # Example staging deployment
    # ssh staging-server "cd /path/to/til && git pull"
    # ssh staging-server "cd /path/to/til && python src/til/production_safe_migration.py til.db"
fi

# Step 3: Post-deployment verification
log_info "Running post-deployment verification..."

# Add verification steps here
# For example:
# - Check database integrity
# - Verify no duplicates
# - Test website functionality

log_info "Deployment to $ENVIRONMENT completed successfully!"

# Step 4: Cleanup old backups (keep last 5)
log_info "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t til-*.db 2>/dev/null | tail -n +6 | xargs -r rm -v

log_info "Deployment process complete!"