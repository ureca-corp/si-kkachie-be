"""add translation thread and category tables

Revision ID: 59725ea892a8
Revises: d7f9g5h6c013
Create Date: 2026-02-03 16:28:02.634621

"""
from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '59725ea892a8'
down_revision: str | Sequence[str] | None = 'd7f9g5h6c013'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Primary Categories 테이블 생성
    op.create_table('translation_primary_categories',
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('name_ko', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('name_en', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('code')
    )

    # 2. Sub Categories 테이블 생성
    op.create_table('translation_sub_categories',
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('name_ko', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('name_en', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('code')
    )

    # 3. Category Mappings 테이블 생성
    op.create_table('translation_category_mappings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('primary_code', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('sub_code', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.ForeignKeyConstraint(['primary_code'], ['translation_primary_categories.code']),
        sa.ForeignKeyConstraint(['sub_code'], ['translation_sub_categories.code']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('primary_code', 'sub_code', name='uq_category_mapping')
    )

    # 4. Context Prompts 테이블 생성
    op.create_table('translation_context_prompts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('primary_code', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('sub_code', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('prompt_ko', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('prompt_en', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('keywords', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['primary_code'], ['translation_primary_categories.code']),
        sa.ForeignKeyConstraint(['sub_code'], ['translation_sub_categories.code']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('primary_code', 'sub_code', name='uq_context_prompt')
    )

    # 5. Translation Threads 테이블 생성
    op.create_table('translation_threads',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('profile_id', sa.Uuid(), nullable=False),
        sa.Column('primary_category', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('sub_category', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['primary_category'], ['translation_primary_categories.code']),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sub_category'], ['translation_sub_categories.code']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_translation_threads_created_at'), 'translation_threads', ['created_at'], unique=False)
    op.create_index(op.f('ix_translation_threads_profile_id'), 'translation_threads', ['profile_id'], unique=False)

    # 6. translations 테이블에 신규 컬럼 추가
    op.add_column('translations', sa.Column('thread_id', sa.Uuid(), nullable=True))
    op.add_column('translations', sa.Column('context_primary', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True))
    op.add_column('translations', sa.Column('context_sub', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True))
    op.create_index(op.f('ix_translations_thread_id'), 'translations', ['thread_id'], unique=False)
    op.create_foreign_key('fk_translations_thread_id', 'translations', 'translation_threads', ['thread_id'], ['id'], ondelete='SET NULL')

    # ─────────────────────────────────────────────────
    # SEED DATA
    # ─────────────────────────────────────────────────

    # Primary Categories (1차 카테고리 - 장소 유형)
    primary_categories_table = sa.table(
        'translation_primary_categories',
        sa.column('code', sa.String),
        sa.column('name_ko', sa.String),
        sa.column('name_en', sa.String),
        sa.column('display_order', sa.Integer),
        sa.column('is_active', sa.Boolean),
    )
    op.bulk_insert(primary_categories_table, [
        {'code': 'FD6', 'name_ko': '음식점', 'name_en': 'Restaurant', 'display_order': 1, 'is_active': True},
        {'code': 'CE7', 'name_ko': '카페', 'name_en': 'Cafe', 'display_order': 2, 'is_active': True},
        {'code': 'HP8', 'name_ko': '병원', 'name_en': 'Hospital', 'display_order': 3, 'is_active': True},
        {'code': 'PM9', 'name_ko': '약국', 'name_en': 'Pharmacy', 'display_order': 4, 'is_active': True},
        {'code': 'MT1', 'name_ko': '대형마트', 'name_en': 'Mart', 'display_order': 5, 'is_active': True},
        {'code': 'CS2', 'name_ko': '편의점', 'name_en': 'Convenience Store', 'display_order': 6, 'is_active': True},
        {'code': 'BK9', 'name_ko': '은행', 'name_en': 'Bank', 'display_order': 7, 'is_active': True},
        {'code': 'SW8', 'name_ko': '지하철역', 'name_en': 'Subway', 'display_order': 8, 'is_active': True},
        {'code': 'AD5', 'name_ko': '숙박', 'name_en': 'Hotel', 'display_order': 9, 'is_active': True},
        {'code': 'AT4', 'name_ko': '관광명소', 'name_en': 'Attraction', 'display_order': 10, 'is_active': True},
        {'code': 'GEN', 'name_ko': '일반', 'name_en': 'General', 'display_order': 99, 'is_active': True},
    ])

    # Sub Categories (2차 카테고리 - 상황/의도)
    sub_categories_table = sa.table(
        'translation_sub_categories',
        sa.column('code', sa.String),
        sa.column('name_ko', sa.String),
        sa.column('name_en', sa.String),
        sa.column('display_order', sa.Integer),
        sa.column('is_active', sa.Boolean),
    )
    op.bulk_insert(sub_categories_table, [
        {'code': 'ordering', 'name_ko': '주문', 'name_en': 'Ordering', 'display_order': 1, 'is_active': True},
        {'code': 'payment', 'name_ko': '결제', 'name_en': 'Payment', 'display_order': 2, 'is_active': True},
        {'code': 'complaint', 'name_ko': '불만', 'name_en': 'Complaint', 'display_order': 3, 'is_active': True},
        {'code': 'reservation', 'name_ko': '예약', 'name_en': 'Reservation', 'display_order': 4, 'is_active': True},
        {'code': 'reception', 'name_ko': '접수', 'name_en': 'Reception', 'display_order': 5, 'is_active': True},
        {'code': 'symptom_explain', 'name_ko': '증상설명', 'name_en': 'Symptom Explanation', 'display_order': 6, 'is_active': True},
        {'code': 'buy_medicine', 'name_ko': '약구매', 'name_en': 'Buy Medicine', 'display_order': 7, 'is_active': True},
        {'code': 'find_item', 'name_ko': '물건찾기', 'name_en': 'Find Item', 'display_order': 8, 'is_active': True},
        {'code': 'exchange_refund', 'name_ko': '교환/환불', 'name_en': 'Exchange/Refund', 'display_order': 9, 'is_active': True},
        {'code': 'inquiry', 'name_ko': '문의', 'name_en': 'Inquiry', 'display_order': 10, 'is_active': True},
        {'code': 'other', 'name_ko': '기타', 'name_en': 'Other', 'display_order': 99, 'is_active': True},
    ])

    # Category Mappings (1차-2차 카테고리 매핑)
    mappings_table = sa.table(
        'translation_category_mappings',
        sa.column('id', sa.Uuid),
        sa.column('primary_code', sa.String),
        sa.column('sub_code', sa.String),
    )
    mappings = [
        # FD6 (음식점): ordering, payment, complaint, reservation, inquiry, other
        ('FD6', 'ordering'), ('FD6', 'payment'), ('FD6', 'complaint'),
        ('FD6', 'reservation'), ('FD6', 'inquiry'), ('FD6', 'other'),
        # CE7 (카페): ordering, payment, complaint, inquiry, other
        ('CE7', 'ordering'), ('CE7', 'payment'), ('CE7', 'complaint'),
        ('CE7', 'inquiry'), ('CE7', 'other'),
        # HP8 (병원): reception, symptom_explain, payment, inquiry, other
        ('HP8', 'reception'), ('HP8', 'symptom_explain'), ('HP8', 'payment'),
        ('HP8', 'inquiry'), ('HP8', 'other'),
        # PM9 (약국): symptom_explain, buy_medicine, payment, inquiry, other
        ('PM9', 'symptom_explain'), ('PM9', 'buy_medicine'), ('PM9', 'payment'),
        ('PM9', 'inquiry'), ('PM9', 'other'),
        # MT1 (대형마트): find_item, payment, exchange_refund, inquiry, other
        ('MT1', 'find_item'), ('MT1', 'payment'), ('MT1', 'exchange_refund'),
        ('MT1', 'inquiry'), ('MT1', 'other'),
        # CS2 (편의점): find_item, payment, exchange_refund, inquiry, other
        ('CS2', 'find_item'), ('CS2', 'payment'), ('CS2', 'exchange_refund'),
        ('CS2', 'inquiry'), ('CS2', 'other'),
        # BK9 (은행): inquiry, other
        ('BK9', 'inquiry'), ('BK9', 'other'),
        # SW8 (지하철역): inquiry, other
        ('SW8', 'inquiry'), ('SW8', 'other'),
        # AD5 (숙박): reservation, payment, inquiry, other
        ('AD5', 'reservation'), ('AD5', 'payment'), ('AD5', 'inquiry'), ('AD5', 'other'),
        # AT4 (관광명소): inquiry, other
        ('AT4', 'inquiry'), ('AT4', 'other'),
        # GEN (일반): inquiry, other
        ('GEN', 'inquiry'), ('GEN', 'other'),
    ]
    op.bulk_insert(mappings_table, [
        {'id': str(uuid4()), 'primary_code': p, 'sub_code': s}
        for p, s in mappings
    ])

    # Context Prompts (AI 번역 컨텍스트 프롬프트)
    prompts_table = sa.table(
        'translation_context_prompts',
        sa.column('id', sa.Uuid),
        sa.column('primary_code', sa.String),
        sa.column('sub_code', sa.String),
        sa.column('prompt_ko', sa.String),
        sa.column('prompt_en', sa.String),
        sa.column('keywords', sa.String),
        sa.column('is_active', sa.Boolean),
    )
    prompts = [
        # 음식점 (FD6)
        ('FD6', 'ordering', '음식점에서 음식을 주문하는 상황입니다. 메뉴 관련 표현을 정확하게 번역해주세요.', 'This is a situation of ordering food at a restaurant. Please translate menu-related expressions accurately.', '메뉴,주문,추천,매운,달콤'),
        ('FD6', 'payment', '음식점에서 결제하는 상황입니다. 결제 방식과 금액 관련 표현을 정확하게 번역해주세요.', 'This is a payment situation at a restaurant. Please translate payment method and amount expressions accurately.', '카드,현금,계산,영수증'),
        ('FD6', 'complaint', '음식점에서 불만을 제기하는 상황입니다. 정중하면서도 명확한 표현으로 번역해주세요.', 'This is a complaint situation at a restaurant. Please translate with polite but clear expressions.', '문제,교환,환불,매니저'),
        ('FD6', 'reservation', '음식점에서 예약하는 상황입니다. 날짜, 시간, 인원 관련 표현을 정확하게 번역해주세요.', 'This is a reservation situation at a restaurant. Please translate date, time, and party size expressions accurately.', '예약,취소,시간,인원'),
        # 카페 (CE7)
        ('CE7', 'ordering', '카페에서 음료를 주문하는 상황입니다. 음료 옵션 관련 표현을 정확하게 번역해주세요.', 'This is a situation of ordering drinks at a cafe. Please translate drink option expressions accurately.', '커피,사이즈,얼음,시럽'),
        ('CE7', 'payment', '카페에서 결제하는 상황입니다. 결제 방식 관련 표현을 정확하게 번역해주세요.', 'This is a payment situation at a cafe. Please translate payment method expressions accurately.', '카드,현금,포인트'),
        # 병원 (HP8)
        ('HP8', 'reception', '병원에서 접수하는 상황입니다. 보험, 예약 관련 표현을 정확하게 번역해주세요.', 'This is a reception situation at a hospital. Please translate insurance and appointment expressions accurately.', '접수,보험,예약,진료'),
        ('HP8', 'symptom_explain', '병원에서 증상을 설명하는 상황입니다. 의료 용어와 증상 표현을 정확하게 번역해주세요.', 'This is a situation of explaining symptoms at a hospital. Please translate medical terms and symptom expressions accurately.', '통증,열,기침,두통,어지러움'),
        # 약국 (PM9)
        ('PM9', 'symptom_explain', '약국에서 증상을 설명하는 상황입니다. 일반적인 증상 표현을 정확하게 번역해주세요.', 'This is a situation of explaining symptoms at a pharmacy. Please translate common symptom expressions accurately.', '통증,감기,소화,알레르기'),
        ('PM9', 'buy_medicine', '약국에서 약을 구매하는 상황입니다. 약품 관련 표현을 정확하게 번역해주세요.', 'This is a situation of buying medicine at a pharmacy. Please translate medicine-related expressions accurately.', '진통제,감기약,연고,처방전'),
        # 마트/편의점 (MT1, CS2)
        ('MT1', 'find_item', '마트에서 물건을 찾는 상황입니다. 위치와 상품 관련 표현을 정확하게 번역해주세요.', 'This is a situation of finding items at a mart. Please translate location and product expressions accurately.', '어디,위치,코너,매대'),
        ('CS2', 'find_item', '편의점에서 물건을 찾는 상황입니다. 간단한 위치 표현을 정확하게 번역해주세요.', 'This is a situation of finding items at a convenience store. Please translate simple location expressions accurately.', '어디,위치'),
        # 숙박 (AD5)
        ('AD5', 'reservation', '호텔에서 예약하는 상황입니다. 날짜, 객실 타입 관련 표현을 정확하게 번역해주세요.', 'This is a reservation situation at a hotel. Please translate date and room type expressions accurately.', '체크인,체크아웃,객실,예약'),
        # 일반 (공통)
        ('GEN', 'inquiry', '일반적인 문의 상황입니다. 질문과 답변 표현을 정확하게 번역해주세요.', 'This is a general inquiry situation. Please translate question and answer expressions accurately.', '질문,도움,정보'),
    ]
    op.bulk_insert(prompts_table, [
        {'id': str(uuid4()), 'primary_code': p, 'sub_code': s, 'prompt_ko': ko, 'prompt_en': en, 'keywords': kw, 'is_active': True}
        for p, s, ko, en, kw in prompts
    ])


def downgrade() -> None:
    """Downgrade schema."""
    # translations 테이블 컬럼 제거
    op.drop_constraint('fk_translations_thread_id', 'translations', type_='foreignkey')
    op.drop_index(op.f('ix_translations_thread_id'), table_name='translations')
    op.drop_column('translations', 'context_sub')
    op.drop_column('translations', 'context_primary')
    op.drop_column('translations', 'thread_id')

    # 테이블 삭제 (역순)
    op.drop_index(op.f('ix_translation_threads_profile_id'), table_name='translation_threads')
    op.drop_index(op.f('ix_translation_threads_created_at'), table_name='translation_threads')
    op.drop_table('translation_threads')
    op.drop_table('translation_context_prompts')
    op.drop_table('translation_category_mappings')
    op.drop_table('translation_sub_categories')
    op.drop_table('translation_primary_categories')
