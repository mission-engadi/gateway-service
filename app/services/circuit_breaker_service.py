"""Circuit Breaker Service - Implement circuit breaker pattern"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerService:
    """Service for implementing circuit breaker pattern"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60
    ):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            success_threshold: Number of successes to close circuit from half-open
            timeout: Seconds to wait before trying half-open state
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        # Circuit states per service
        self._circuits: Dict[str, Dict] = {}
    
    def _get_circuit(self, service_name: str) -> Dict:
        """Get or create circuit for a service"""
        if service_name not in self._circuits:
            self._circuits[service_name] = {
                'state': CircuitState.CLOSED,
                'failure_count': 0,
                'success_count': 0,
                'last_failure_time': None,
                'last_state_change': datetime.utcnow()
            }
        return self._circuits[service_name]
    
    def is_available(self, service_name: str) -> bool:
        """Check if service is available for requests
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if service is available, False otherwise
        """
        circuit = self._get_circuit(service_name)
        
        # If circuit is closed, always available
        if circuit['state'] == CircuitState.CLOSED:
            return True
        
        # If circuit is open, check if timeout expired
        if circuit['state'] == CircuitState.OPEN:
            if circuit['last_failure_time']:
                elapsed = (datetime.utcnow() - circuit['last_failure_time']).seconds
                if elapsed >= self.timeout:
                    # Try half-open
                    circuit['state'] = CircuitState.HALF_OPEN
                    circuit['success_count'] = 0
                    circuit['last_state_change'] = datetime.utcnow()
                    return True
            return False
        
        # If half-open, allow requests to test
        return True
    
    def record_success(self, service_name: str):
        """Record successful request
        
        Args:
            service_name: Name of the service
        """
        circuit = self._get_circuit(service_name)
        
        if circuit['state'] == CircuitState.HALF_OPEN:
            circuit['success_count'] += 1
            
            # If enough successes, close the circuit
            if circuit['success_count'] >= self.success_threshold:
                circuit['state'] = CircuitState.CLOSED
                circuit['failure_count'] = 0
                circuit['success_count'] = 0
                circuit['last_state_change'] = datetime.utcnow()
        
        elif circuit['state'] == CircuitState.CLOSED:
            # Reset failure count on success
            circuit['failure_count'] = max(0, circuit['failure_count'] - 1)
    
    def record_failure(self, service_name: str):
        """Record failed request
        
        Args:
            service_name: Name of the service
        """
        circuit = self._get_circuit(service_name)
        circuit['failure_count'] += 1
        circuit['last_failure_time'] = datetime.utcnow()
        
        # If half-open and failed, go back to open
        if circuit['state'] == CircuitState.HALF_OPEN:
            circuit['state'] = CircuitState.OPEN
            circuit['success_count'] = 0
            circuit['last_state_change'] = datetime.utcnow()
        
        # If closed and reached threshold, open the circuit
        elif circuit['state'] == CircuitState.CLOSED:
            if circuit['failure_count'] >= self.failure_threshold:
                circuit['state'] = CircuitState.OPEN
                circuit['last_state_change'] = datetime.utcnow()
    
    def get_state(self, service_name: str) -> CircuitState:
        """Get current circuit state
        
        Args:
            service_name: Name of the service
            
        Returns:
            Current circuit state
        """
        circuit = self._get_circuit(service_name)
        return circuit['state']
    
    def reset(self, service_name: str):
        """Reset circuit breaker for a service
        
        Args:
            service_name: Name of the service
        """
        if service_name in self._circuits:
            self._circuits[service_name] = {
                'state': CircuitState.CLOSED,
                'failure_count': 0,
                'success_count': 0,
                'last_failure_time': None,
                'last_state_change': datetime.utcnow()
            }
    
    def get_circuit_info(self, service_name: str) -> Dict:
        """Get detailed circuit information
        
        Args:
            service_name: Name of the service
            
        Returns:
            Circuit information
        """
        circuit = self._get_circuit(service_name)
        return {
            'service_name': service_name,
            'state': circuit['state'],
            'failure_count': circuit['failure_count'],
            'success_count': circuit['success_count'],
            'last_failure_time': circuit['last_failure_time'],
            'last_state_change': circuit['last_state_change'],
            'is_available': self.is_available(service_name)
        }
