
import tcp_cmd_fun as tcmdf


def get_sus_cg_height(model_name):

    return tcmdf.get_variable(f'.{model_name}.testrig.pvs_cg_height')


def get_sus_wheelbase(model_name):

    return tcmdf.get_variable(f'.{model_name}.testrig.pvs_wheelbase')


def get_sus_sprung_mass(model_name):

    return tcmdf.get_variable(f'.{model_name}.testrig.pvs_total_sprung_mass')

def get_sus_wheel_mass(model_name):

    return tcmdf.get_variable(f'.{model_name}.testrig.pvs_wheel_mass')  




# return tcmdf.get_variable(f'.{model_name}.testrig.pvs_max_jack_force')    


# def get_tire_unloaded_radius(model_name):
# 
#   return tcmdf.get_variable(f'.{model_name}.testrig.')



model_name = tcmdf.get_current_model()
cg_height = get_sus_cg_height(model_name)
wheelbase = get_sus_wheelbase(model_name)
sprung_mass = get_sus_sprung_mass(model_name)
wheel_mass = get_sus_wheel_mass(model_name)

print(cg_height, wheelbase, sprung_mass, wheel_mass)
print(tcmdf.get_model_sus_tire_data(model_name))

