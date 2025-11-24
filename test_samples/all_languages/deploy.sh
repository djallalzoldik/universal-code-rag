#!/bin/bash
# Complex Bash script with advanced features

set -euo pipefail

# Global variables
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/deploy.log"
declare -A CONFIG

# Function definitions
log_message() {
    local level="$1"
    shift
    local message="$*"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

check_dependencies() {
    local dependencies=("docker" "kubectl" "helm")
    
    for dep in "${dependencies[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_message "ERROR" "$dep is not installed"
            return 1
        fi
    done
    log_message "INFO" "All dependencies found"
}

parse_config() {
    local config_file="$1"
    
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        CONFIG["$key"]="$value"
    done < "$config_file"
}

deploy_application() {
    local environment="$1"
    local version="${2:-latest}"
    
    log_message "INFO" "Deploying to $environment with version $version"
    
    case "$environment" in
        prod|production)
            kubectl apply -f manifests/production/ --namespace=prod
            ;;
        staging)
            kubectl apply -f manifests/staging/ --namespace=staging
            ;;
        *)
            log_message "ERROR" "Unknown environment: $environment"
            return 1
            ;;
    esac
    
    # Wait for deployment
    kubectl rollout status deployment/my-app -n "$environment" --timeout=5m
}

cleanup() {
    log_message "INFO" "Cleaning up resources"
    rm -f /tmp/deploy-*.tmp
}

# Trap errors
trap cleanup EXIT ERR

# Main execution
main() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 <environment> <version>"
        exit 1
    fi
    
    check_dependencies || exit 1
    parse_config "${SCRIPT_DIR}/config.ini"
    deploy_application "$1" "$2"
    
    log_message "SUCCESS" "Deployment completed"
}

main "$@"
