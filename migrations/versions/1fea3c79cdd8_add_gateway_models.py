"""Add gateway models: RouteConfig, RateLimitRule, GatewayLog, ServiceHealth

Revision ID: 1fea3c79cdd8
Revises: 
Create Date: 2025-12-25 00:32:32.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1fea3c79cdd8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE limittype AS ENUM ('per_user', 'per_ip', 'per_endpoint', 'global')")
    op.execute("CREATE TYPE servicestatus AS ENUM ('healthy', 'unhealthy', 'degraded', 'unknown')")
    
    # Create route_configs table
    op.create_table('route_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('path_pattern', sa.String(), nullable=False),
        sa.Column('target_service', sa.String(), nullable=False),
        sa.Column('target_url', sa.String(), nullable=False),
        sa.Column('methods', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('circuit_breaker_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_route_configs_is_active'), 'route_configs', ['is_active'], unique=False)
    op.create_index(op.f('ix_route_configs_path_pattern'), 'route_configs', ['path_pattern'], unique=True)
    op.create_index(op.f('ix_route_configs_priority'), 'route_configs', ['priority'], unique=False)
    
    # Create rate_limit_rules table
    op.create_table('rate_limit_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_name', sa.String(), nullable=False),
        sa.Column('limit_type', sa.Enum('per_user', 'per_ip', 'per_endpoint', 'global', name='limittype'), nullable=False),
        sa.Column('path_pattern', sa.String(), nullable=True),
        sa.Column('max_requests', sa.Integer(), nullable=False),
        sa.Column('window_seconds', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rate_limit_rules_is_active'), 'rate_limit_rules', ['is_active'], unique=False)
    op.create_index(op.f('ix_rate_limit_rules_limit_type'), 'rate_limit_rules', ['limit_type'], unique=False)
    op.create_index(op.f('ix_rate_limit_rules_rule_name'), 'rate_limit_rules', ['rule_name'], unique=True)
    
    # Create gateway_logs table
    op.create_table('gateway_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('target_service', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('client_ip', sa.String(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gateway_logs_client_ip'), 'gateway_logs', ['client_ip'], unique=False)
    op.create_index(op.f('ix_gateway_logs_created_at'), 'gateway_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_gateway_logs_path'), 'gateway_logs', ['path'], unique=False)
    op.create_index(op.f('ix_gateway_logs_request_id'), 'gateway_logs', ['request_id'], unique=False)
    op.create_index(op.f('ix_gateway_logs_target_service'), 'gateway_logs', ['target_service'], unique=False)
    op.create_index(op.f('ix_gateway_logs_user_id'), 'gateway_logs', ['user_id'], unique=False)
    
    # Create service_health table
    op.create_table('service_health',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_name', sa.String(), nullable=False),
        sa.Column('service_url', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('healthy', 'unhealthy', 'degraded', 'unknown', name='servicestatus'), nullable=False),
        sa.Column('last_check_at', sa.DateTime(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('circuit_open', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_health_circuit_open'), 'service_health', ['circuit_open'], unique=False)
    op.create_index(op.f('ix_service_health_service_name'), 'service_health', ['service_name'], unique=True)
    op.create_index(op.f('ix_service_health_status'), 'service_health', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_service_health_status'), table_name='service_health')
    op.drop_index(op.f('ix_service_health_service_name'), table_name='service_health')
    op.drop_index(op.f('ix_service_health_circuit_open'), table_name='service_health')
    op.drop_table('service_health')
    
    op.drop_index(op.f('ix_gateway_logs_user_id'), table_name='gateway_logs')
    op.drop_index(op.f('ix_gateway_logs_target_service'), table_name='gateway_logs')
    op.drop_index(op.f('ix_gateway_logs_request_id'), table_name='gateway_logs')
    op.drop_index(op.f('ix_gateway_logs_path'), table_name='gateway_logs')
    op.drop_index(op.f('ix_gateway_logs_created_at'), table_name='gateway_logs')
    op.drop_index(op.f('ix_gateway_logs_client_ip'), table_name='gateway_logs')
    op.drop_table('gateway_logs')
    
    op.drop_index(op.f('ix_rate_limit_rules_rule_name'), table_name='rate_limit_rules')
    op.drop_index(op.f('ix_rate_limit_rules_limit_type'), table_name='rate_limit_rules')
    op.drop_index(op.f('ix_rate_limit_rules_is_active'), table_name='rate_limit_rules')
    op.drop_table('rate_limit_rules')
    
    op.drop_index(op.f('ix_route_configs_priority'), table_name='route_configs')
    op.drop_index(op.f('ix_route_configs_path_pattern'), table_name='route_configs')
    op.drop_index(op.f('ix_route_configs_is_active'), table_name='route_configs')
    op.drop_table('route_configs')
    
    # Drop enum types
    op.execute("DROP TYPE servicestatus")
    op.execute("DROP TYPE limittype")
