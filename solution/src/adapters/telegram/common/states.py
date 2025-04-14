from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    choosing_action = State()
    entering_advertiser_name = State()
    entering_advertiser_id = State()
    entering_ml_score = State()
    entering_client_id = State()


class CampaignCreationStates(StatesGroup):
    entering_title = State()
    entering_text = State()
    entering_impressions_limit = State()
    entering_clicks_limit = State()
    entering_cost_per_impression = State()
    entering_cost_per_click = State()
    entering_start_date = State()
    entering_end_date = State()
    entering_gender = State()
    entering_age_from = State()
    entering_age_to = State()
    entering_location = State()
    confirming_targeting = State()
    uploading_image = State()
    confirming_creation = State()


class CampaignEditStates(StatesGroup):
    choosing_field = State()
    entering_title = State()
    entering_text = State()
    entering_costs = State()
    entering_targeting = State()
    confirming_update = State()


class CampaignImageStates(StatesGroup):
    choosing_action = State()
    uploading_image = State()
    confirming_delete = State()


class CampaignManagementStates(StatesGroup):
    choosing_action = State()
    entering_campaign_id = State()
    confirming_delete = State()
    viewing_list = State()
    viewing_details = State()


class TargetingStates(StatesGroup):
    entering_gender = State()
    entering_age_from = State()
    entering_age_to = State()
    entering_location = State()
    confirming_targeting = State()
