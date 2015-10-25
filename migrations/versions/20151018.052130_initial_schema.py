"""initial schema

Revision ID: 56ab2fd6d22
Revises: None
Create Date: 2015-10-18 05:21:30.598826

"""

# revision identifiers, used by Alembic.
revision = '56ab2fd6d22'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def create_table(table_name, *args, **kwargs):
    op.create_table(table_name,
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('created_at', sa.DateTime(True),
                              server_default=sa.func.now()),
                    sa.Column('updated_at', sa.DateTime(True),
                              server_default=sa.func.now()),
                    *args, **kwargs)

def upgrade():
    create_table('color',
                 sa.Column('name', sa.String(length=32), nullable=True),
                 sa.Column('code', sa.String(length=8), nullable=True),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('code'))

    create_table('family',
                 sa.Column('family', sa.String(length=45), nullable=False),
                 sa.Column('qualifier',
                           sa.Enum('s. lat.', 's. str.', name='family_qualifier_type'),
                           nullable=True),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('family', 'qualifier'))

    op.create_index(op.f('ix_family_family'), 'family', ['family'], unique=False)

    create_table('geography',
                 sa.Column('name', sa.String(length=255), nullable=False),
                 sa.Column('tdwg_code', sa.String(length=6), nullable=True),
                 sa.Column('iso_code', sa.String(length=7), nullable=True),
                 sa.Column('parent_id', sa.Integer(), nullable=True),
                 sa.ForeignKeyConstraint(['parent_id'], ['geography.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('habit',
                 sa.Column('name', sa.String(length=64), nullable=True),
                 sa.Column('code', sa.String(length=8), nullable=True),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('code'))

    create_table('location',
                 sa.Column('code', sa.String(length=10), nullable=False),
                 sa.Column('name', sa.String(length=64), nullable=True),
                 sa.Column('description', sa.Text(), nullable=True),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('code'))

    create_table('organization',
                 sa.Column('name', sa.String(), nullable=True),
                 sa.Column('short_name', sa.String(), nullable=True),
                 sa.Column('pg_user', sa.String(), nullable=True),
                 sa.Column('pg_schema', sa.String(), nullable=True),
                 sa.Column('address', sa.String(), nullable=True),
                 sa.Column('city', sa.String(), nullable=True),
                 sa.Column('state', sa.String(), nullable=True),
                 sa.Column('zip', sa.String(), nullable=True),
                 sa.Column('date_approved', sa.DateTime(timezone=True), nullable=True),
                 sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
                 sa.Column('date_suspended', sa.DateTime(timezone=True), nullable=True),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('pg_schema'),
                 sa.UniqueConstraint('pg_user'))

    create_table('propagation',
                 sa.Column('prop_type',
                           sa.Enum('Other', 'UnrootedCutting', 'Seed',
                                   name='propagation_prop_type_type'),
                           nullable=False),
                 sa.Column('notes', sa.Text(), nullable=True),
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.PrimaryKeyConstraint('id'))

    create_table('report',
                 sa.Column('name', sa.String(), nullable=False),
                 sa.Column('query', sa.String(), nullable=True),
                 sa.Column('setting', postgresql.JSON(), nullable=True),
                 sa.PrimaryKeyConstraint('id'))

    op.create_index(op.f('ix_report_name'), 'report', ['name'], unique=True)

    create_table('source_detail',
                 sa.Column('name', sa.String(length=75), nullable=True),
                 sa.Column('description', sa.Text(), nullable=True),
                 sa.Column('source_type',
                           sa.Enum('Research/FieldStation', 'UniversityDepartment',
                                   'Individual', 'Other', 'Commercial', 'Staff',
                                   'GeneBank', 'BG', 'Expedition', 'Unknown',
                                   'MunicipalDepartment', 'Club',
                                   name='source_detail_source_type_type'),
                           nullable=True),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('name'))

    create_table('family_note',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('user', sa.String(length=64), nullable=True),
                 sa.Column('category', sa.String(length=32), nullable=True),
                 sa.Column('note', sa.Text(), nullable=False),
                 sa.Column('family_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('family_synonym',
                 sa.Column('family_id', sa.Integer(), nullable=False),
                 sa.Column('synonym_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
                 sa.ForeignKeyConstraint(['synonym_id'], ['family.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('synonym_id'))

    create_table('genus',
                 sa.Column('genus', sa.String(length=64), nullable=False),
                 sa.Column('author', sa.String(length=255), nullable=True),
                 sa.Column('qualifier',
                           sa.Enum('s. lat.', 's. str', '', name='genus_qualifier_type'),
                           nullable=True),
                 sa.Column('family_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('genus', 'author', 'qualifier', 'family_id'))

    op.create_index(op.f('ix_genus_genus'), 'genus', ['genus'], unique=False)

    create_table('prop_cutting',
                 sa.Column('cutting_type',
                           sa.Enum('Other', 'InterNodal', 'Nodal',
                                   name='prop_cutting_cutting_type_type'),
                           nullable=True),
                 sa.Column('tip', sa.Enum('Intact', 'Removed', 'None',
                                          name='prop_cutting_tip_type'),
                           nullable=True),
                 sa.Column('leaves', sa.Enum('Intact', 'Removed', 'None',
                                             name='prop_cutting_leaves_type'),
                           nullable=True),
                 sa.Column('leaves_reduced_pct', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('length', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('length_unit', sa.Enum('mm', 'in', 'cm',
                                                  name='prop_cutting_length_unit_type'),
                           nullable=True),
                 sa.Column('wound', sa.Enum('No', 'Double', 'Single', 'Slice',
                                            name='prop_cutting_would_type'),
                           nullable=True),
                 sa.Column('flower_buds', sa.Enum('Removed', 'None',
                                                  name='prop_cutting_flower_buds_type'),
                           nullable=True),
                 sa.Column('fungicide', sa.String(), nullable=True),
                 sa.Column('hormone', sa.String(), nullable=True),
                 sa.Column('media', sa.String(), nullable=True),
                 sa.Column('container', sa.String(), nullable=True),
                 sa.Column('location', sa.String(), nullable=True),
                 sa.Column('cover', sa.String(), nullable=True),
                 sa.Column('bottom_heat_temp', sa.Integer(), autoincrement=False,
                           nullable=True),
                 sa.Column('bottom_heat_unit',
                           sa.Enum('C', 'F', name='prop_cuting_bottom_head_unit_type'),
                           nullable=True),
                 sa.Column('rooted_pct', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('propagation_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['propagation_id'], ['propagation.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('prop_seed',
                 sa.Column('pretreatment', sa.Text(), nullable=True),
                 sa.Column('nseeds', sa.Integer(), autoincrement=False, nullable=False),
                 sa.Column('date_sown', sa.Date(), nullable=False),
                 sa.Column('container', sa.String(), nullable=True),
                 sa.Column('media', sa.String(), nullable=True),
                 sa.Column('covered', sa.String(), nullable=True),
                 sa.Column('location', sa.String(), nullable=True),
                 sa.Column('moved_from', sa.String(), nullable=True),
                 sa.Column('moved_to', sa.String(), nullable=True),
                 sa.Column('moved_date', sa.Date(), nullable=True),
                 sa.Column('germ_date', sa.Date(), nullable=True),
                 sa.Column('nseedlings', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('germ_pct', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('date_planted', sa.Date(), nullable=True),
                 sa.Column('propagation_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['propagation_id'], ['propagation.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('user',
                 sa.Column('username', sa.String(), nullable=False),
                 sa.Column('fullname', sa.String(), nullable=True),
                 sa.Column('title', sa.String(), nullable=True),
                 sa.Column('email', sa.String(), nullable=False),
                 sa.Column('timezone', sa.String(), nullable=True),
                 sa.Column('access_token', sa.String(), nullable=True),
                 sa.Column('access_token_expiration', sa.DateTime(timezone=True), nullable=True),
                 sa.Column('is_sysadmin', sa.Boolean(), nullable=True),
                 sa.Column('is_org_owner', sa.Boolean(), nullable=True),
                 sa.Column('is_org_admin', sa.Boolean(), nullable=True),
                 sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=True),
                 sa.Column('date_suspended', sa.Date(), nullable=True),
                 sa.Column('password_reset_token', sa.String(), nullable=True),
                 sa.Column('password_reset_token_expiration', sa.DateTime(timezone=True),
                           nullable=True),
                 sa.Column('organization_id', sa.Integer(), nullable=True),
                 sa.Column('password', sa.String(), nullable=False),
                 sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('access_token'),
                 sa.UniqueConstraint('email'),
                 sa.UniqueConstraint('username'))

    create_table('genus_note',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('user', sa.String(length=64), nullable=True),
                 sa.Column('category', sa.String(length=32), nullable=True),
                 sa.Column('note', sa.Text(), nullable=False),
                 sa.Column('genus_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['genus_id'], ['genus.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('genus_synonym',
                 sa.Column('genus_id', sa.Integer(), nullable=False),
                 sa.Column('synonym_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['genus_id'], ['genus.id'], ),
                 sa.ForeignKeyConstraint(['synonym_id'], ['genus.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('synonym_id'))

    create_table('invitation',
                 sa.Column('email', sa.String(), nullable=False),
                 sa.Column('token', sa.String(), nullable=False),
                 sa.Column('token_expiration', sa.DateTime(timezone=True), nullable=True),
                 sa.Column('date_sent', sa.DateTime(timezone=True), nullable=False),
                 sa.Column('message', sa.String(), nullable=True),
                 sa.Column('accepted', sa.Boolean(), nullable=True),
                 sa.Column('invited_by_id', sa.Integer(), nullable=False),
                 sa.Column('organization_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['invited_by_id'], ['user.id'], ),
                 sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    op.create_index(op.f('ix_invitation_token'), 'invitation', ['token'], unique=True)

    create_table('prop_rooted',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('quantity', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('cutting_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['cutting_id'], ['prop_cutting.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('taxon',
                 sa.Column('sp', sa.String(length=64), nullable=True),
                 sa.Column('sp2', sa.String(length=64), nullable=True),
                 sa.Column('sp_author', sa.String(length=128), nullable=True),
                 sa.Column('hybrid', sa.Boolean(), nullable=True),
                 sa.Column('sp_qual', sa.Enum('agg.', 's. lat.', 's. str.',
                                              name='taxon_sp_qual_type'),
                           nullable=True),
                 sa.Column('cv_group', sa.String(length=50), nullable=True),
                 sa.Column('trade_name', sa.String(length=64), nullable=True),
                 sa.Column('infrasp1', sa.String(length=64), nullable=True),
                 sa.Column('infrasp1_rank',
                           sa.Enum('var.', 'subsp.', 'subvar.', 'f.', 'subf.', 'cv.',
                                   name='infrasp_rank_type'), nullable=True),
                 sa.Column('infrasp1_author', sa.String(length=64), nullable=True),
                 sa.Column('infrasp2', sa.String(length=64), nullable=True),
                 sa.Column('infrasp2_rank',
                           sa.Enum('var.', 'subsp.', 'subvar.', 'f.', 'subf.', 'cv.',
                                   name='infrasp_rank_type'), nullable=True),
                 sa.Column('infrasp2_author', sa.String(length=64), nullable=True),
                 sa.Column('infrasp3', sa.String(length=64), nullable=True),
                 sa.Column('infrasp3_rank',
                           sa.Enum('var.', 'subsp.', 'subvar.', 'f.', 'subf.', 'cv.',
                                   name='infrasp_rank_type'), nullable=True),
                 sa.Column('infrasp3_author', sa.String(length=64), nullable=True),
                 sa.Column('infrasp4', sa.String(length=64), nullable=True),
                 sa.Column('infrasp4_rank',
                           sa.Enum('var.', 'subsp.', 'subvar.', 'f.', 'subf.', 'cv.',
                                   name='infrasp_rank_type'), nullable=True),
                 sa.Column('infrasp4_author', sa.String(length=64), nullable=True),
                 sa.Column('genus_id', sa.Integer(), nullable=False),
                 sa.Column('label_distribution', sa.Text(), nullable=True),
                 sa.Column('habit_id', sa.Integer(), nullable=True),
                 sa.Column('flower_color_id', sa.Integer(), nullable=True),
                 sa.Column('awards', sa.Text(), nullable=True),
                 sa.ForeignKeyConstraint(['flower_color_id'], ['color.id'], ),
                 sa.ForeignKeyConstraint(['genus_id'], ['genus.id'], ),
                 sa.ForeignKeyConstraint(['habit_id'], ['habit.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    op.create_index(op.f('ix_taxon_sp'), 'taxon', ['sp'], unique=False)
    op.create_index(op.f('ix_taxon_sp2'), 'taxon', ['sp2'], unique=False)

    create_table('accession',
                 sa.Column('code', sa.String(length=20), nullable=False),
                 sa.Column('prov_type',
                           sa.Enum('InsufficientData', 'Cultivated', 'Unknown', 'NotWild',
                                   'Wild', name='accession_prov_type_type'),
                           nullable=True),
                 sa.Column('wild_prov_status',
                           sa.Enum('WildNonNative', 'InsufficientData', 'WildNative',
                                   'Unknown', 'CultivatedNative',
                                   name='accession_wild_prov_status_type'),
                           nullable=True),
                 sa.Column('date_accd', sa.Date(), nullable=True),
                 sa.Column('date_recvd', sa.Date(), nullable=True),
                 sa.Column('quantity_recvd', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('recvd_type',
                           sa.Enum('DIVI', 'BUDC', 'RHIZ', 'RCUT', 'UNKN', 'BUDD', 'PLNT',
                                   'CLUM', 'CORM', 'SEDL', 'BBIL', 'GRAF', 'BULB', 'TUBE',
                                   'LAYE', 'BRPL', 'SPOR', 'PSBU', 'ROOT', 'SEED', 'VEGS',
                                   'URCU', 'SCIO', 'SPRL', 'SCKR', 'ALAY', 'ROOC', 'BBPL',
                                   name='accession_recvd_type_type'),
                           nullable=True),
                 sa.Column('id_qual',
                           sa.Enum('aff.', 'cf.', 'incorrect', 'forsan', 'near', '?',
                                   name='accession_id_qual_type'),
                           nullable=True),
                 sa.Column('id_qual_rank', sa.String(length=10), nullable=True),
                 sa.Column('private', sa.Boolean(), nullable=True),
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.Column('intended_location_id', sa.Integer(), nullable=True),
                 sa.Column('intended2_location_id', sa.Integer(), nullable=True),
                 sa.ForeignKeyConstraint(['intended2_location_id'], ['location.id'], ),
                 sa.ForeignKeyConstraint(['intended_location_id'], ['location.id'], ),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('code'))

    create_table('taxon_distribution',
                 sa.Column('geography_id', sa.Integer(), nullable=False),
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['geography_id'], ['geography.id'], ),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('taxon_note',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('user', sa.String(length=64), nullable=True),
                 sa.Column('category', sa.String(length=32), nullable=True),
                 sa.Column('note', sa.Text(), nullable=False),
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('taxon_synonym',
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.Column('synonym_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['synonym_id'], ['taxon.id'], ),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('synonym_id'))

    create_table('vernacular_name',
                 sa.Column('name', sa.String(length=128), nullable=False),
                 sa.Column('language', sa.String(length=128), nullable=True),
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('name', 'language', 'taxon_id', name='vn_index'))

    create_table('accession_note',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('user', sa.String(length=64), nullable=True),
                 sa.Column('category', sa.String(length=32), nullable=True),
                 sa.Column('note', sa.Text(), nullable=False),
                 sa.Column('accession_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['accession_id'], ['accession.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('default_vernacular_name',
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.Column('vernacular_name_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.ForeignKeyConstraint(['vernacular_name_id'], ['vernacular_name.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('taxon_id', 'vernacular_name_id', name='default_vn_index'))

    create_table('plant',
                 sa.Column('code', sa.String(length=6), nullable=False),
                 sa.Column('acc_type',
                           sa.Enum('Vegetative', 'Other', 'Plant', 'Seed', 'Tissue',
                                   name='plant_acc_type_type'),
                           nullable=True),
                 sa.Column('memorial', sa.Boolean(), nullable=True),
                 sa.Column('quantity', sa.Integer(), autoincrement=False, nullable=False),
                 sa.Column('accession_id', sa.Integer(), nullable=False),
                 sa.Column('location_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['accession_id'], ['accession.id'], ),
                 sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('code', 'accession_id'))

    create_table('verification',
                 sa.Column('verifier', sa.String(length=64), nullable=False),
                 sa.Column('date', sa.Date(), nullable=False),
                 sa.Column('reference', sa.Text(), nullable=True),
                 sa.Column('accession_id', sa.Integer(), nullable=False),
                 sa.Column('level', sa.Integer(), autoincrement=False, nullable=False),
                 sa.Column('taxon_id', sa.Integer(), nullable=False),
                 sa.Column('prev_taxon_id', sa.Integer(), nullable=False),
                 sa.Column('notes', sa.Text(), nullable=True),
                 sa.ForeignKeyConstraint(['accession_id'], ['accession.id'], ),
                 sa.ForeignKeyConstraint(['prev_taxon_id'], ['taxon.id'], ),
                 sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('voucher',
                 sa.Column('herbarium', sa.String(), nullable=False),
                 sa.Column('code', sa.String(length=32), nullable=False),
                 sa.Column('parent_material', sa.Boolean(), nullable=True),
                 sa.Column('accession_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['accession_id'], ['accession.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('plant_note',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('user', sa.String(), nullable=True),
                 sa.Column('category', sa.String(), nullable=True),
                 sa.Column('note', sa.Text(), nullable=False),
                 sa.Column('plant_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['plant_id'], ['plant.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('plant_propagation',
                 sa.Column('plant_id', sa.Integer(), nullable=False),
                 sa.Column('propagation_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['plant_id'], ['plant.id'], ),
                 sa.ForeignKeyConstraint(['propagation_id'], ['propagation.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('plant_status',
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('condition',
                           sa.Enum('Poor', 'Indistinguishable', 'Good', 'UnableToLocate',
                                   'Fair', 'Questionable', 'Dead', 'Excellent',
                                   name='plant_status_condition_type'),
                           nullable=True),
                 sa.Column('comment', sa.Text(), nullable=True),
                 sa.Column('checked_by', sa.String(), nullable=True),
                 sa.Column('flowering_status',
                           sa.Enum('Old', 'Immature', 'Flowering',
                                   name='plant_status_flowering_status_type'),
                           nullable=True),
                 sa.Column('fruiting_status',
                           sa.Enum('Unripe', 'Ripe', name='plant_status_fruiting_status_type'),
                           nullable=True),
                 sa.Column('autumn_color_pct', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('leaf_drop_pct', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('leaf_emergence_pct', sa.Integer(), autoincrement=False, nullable=True),
                 sa.Column('sex', sa.Enum('Female', 'Both', 'Male',
                                          name='plant_status_sex_type'),
                           nullable=True),
                 sa.Column('plant_id', sa.Integer(), nullable=False),
                 sa.ForeignKeyConstraint(['plant_id'], ['plant.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('plant_change',
                 sa.Column('plant_id', sa.Integer(), nullable=False),
                 sa.Column('parent_plant_id', sa.Integer(), nullable=True),
                 sa.Column('from_location_id', sa.Integer(), nullable=True),
                 sa.Column('to_location_id', sa.Integer(), nullable=True),
                 sa.Column('person', sa.String(), nullable=True),
                 sa.Column('quantity', sa.Integer(), autoincrement=False, nullable=False),
                 sa.Column('note_id', sa.Integer(), nullable=True),
                 sa.Column('reason',
                           sa.Enum('DEAD', 'DELE', 'DISC', 'DIST', 'DNGM', 'FOGS', 'DISW',
                                   'TOTM', 'WINK', 'OTHR', 'BA40', 'DISN', 'GIVE', 'LOST',
                                   'SUMK', 'PLOP', 'ASS#', 'ERRO', 'STOL',
                                   name='plant_change_type'),
                           nullable=True),
                 sa.Column('date', sa.DateTime(timezone=True), nullable=True),
                 sa.ForeignKeyConstraint(['from_location_id'], ['location.id'], ),
                 sa.ForeignKeyConstraint(['note_id'], ['plant_note.id'], ),
                 sa.ForeignKeyConstraint(['parent_plant_id'], ['plant.id'], ),
                 sa.ForeignKeyConstraint(['plant_id'], ['plant.id'], ),
                 sa.ForeignKeyConstraint(['to_location_id'], ['location.id'], ),
                 sa.PrimaryKeyConstraint('id'))

    create_table('source',
                 sa.Column('sources_code', sa.String(length=32), nullable=True),
                 sa.Column('accession_id', sa.Integer(), nullable=True),
                 sa.Column('source_detail_id', sa.Integer(), nullable=True),
                 sa.Column('propagation_id', sa.Integer(), nullable=True),
                 sa.Column('plant_propagation_id', sa.Integer(), nullable=True),
                 sa.ForeignKeyConstraint(['accession_id'], ['accession.id'], ),
                 sa.ForeignKeyConstraint(['plant_propagation_id'], ['plant_propagation.id'], ),
                 sa.ForeignKeyConstraint(['propagation_id'], ['propagation.id'], ),
                 sa.ForeignKeyConstraint(['source_detail_id'], ['source_detail.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('accession_id'))

    create_table('collection',
                 sa.Column('collector', sa.String(), nullable=True),
                 sa.Column('collectors_code', sa.String(), nullable=True),
                 sa.Column('date', sa.Date(), nullable=True),
                 sa.Column('locale', sa.Text(), nullable=False),
                 sa.Column('latitude', sa.String(length=15), nullable=True),
                 sa.Column('longitude', sa.String(length=15), nullable=True),
                 sa.Column('gps_datum', sa.String(length=32), nullable=True),
                 sa.Column('geo_accy', sa.Float(), nullable=True),
                 sa.Column('elevation', sa.Float(), nullable=True),
                 sa.Column('elevation_accy', sa.Float(), nullable=True),
                 sa.Column('habitat', sa.Text(), nullable=True),
                 sa.Column('notes', sa.Text(), nullable=True),
                 sa.Column('geography_id', sa.Integer(), nullable=True),
                 sa.Column('source_id', sa.Integer(), nullable=True),
                 sa.ForeignKeyConstraint(['geography_id'], ['geography.id'], ),
                 sa.ForeignKeyConstraint(['source_id'], ['source.id'], ),
                 sa.PrimaryKeyConstraint('id'),
                 sa.UniqueConstraint('source_id'))



def downgrade():
    op.drop_table('collection')
    op.drop_table('source')
    op.drop_table('plant_change')
    op.drop_table('plant_status')
    op.drop_table('plant_propagation')
    op.drop_table('plant_note')
    op.drop_table('voucher')
    op.drop_table('verification')
    op.drop_table('plant')
    op.drop_table('default_vernacular_name')
    op.drop_table('accession_note')
    op.drop_table('vernacular_name')
    op.drop_table('taxon_synonym')
    op.drop_table('taxon_note')
    op.drop_table('taxon_distribution')
    op.drop_table('accession')
    op.drop_index(op.f('ix_taxon_sp2'), table_name='taxon')
    op.drop_index(op.f('ix_taxon_sp'), table_name='taxon')
    op.drop_table('taxon')
    op.drop_table('prop_rooted')
    op.drop_index(op.f('ix_invitation_token'), table_name='invitation')
    op.drop_table('invitation')
    op.drop_table('genus_synonym')
    op.drop_table('genus_note')
    op.drop_table('user')
    op.drop_table('prop_seed')
    op.drop_table('prop_cutting')
    op.drop_index(op.f('ix_genus_genus'), table_name='genus')
    op.drop_table('genus')
    op.drop_table('family_synonym')
    op.drop_table('family_note')
    op.drop_table('source_detail')
    op.drop_index(op.f('ix_report_name'), table_name='report')
    op.drop_table('report')
    op.drop_table('propagation')
    op.drop_table('organization')
    op.drop_table('location')
    op.drop_table('habit')
    op.drop_table('geography')
    op.drop_index(op.f('ix_family_family'), table_name='family')
    op.drop_table('family')
    op.drop_table('color')
