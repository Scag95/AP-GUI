import sys
import os

# Aseguramos que Python encuentre la carpeta src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.materials import Concrete01, Steel01, Elastic, Hysteretic, HystereticSM
from src.analysis.sections import AggregatorSection
from src.analysis.element import ForceBeamColumnHinge
from src.analysis.loads import LoadPattern, NodalLoad, ElementLoad

def create_model():
    # 1. Iniciamos un proyecto en blanco
    manager = ProjectManager.instance()
    manager.new_project()
    print("Construyendo modelo de calibración...")

    # ==========================================
    # 1. NODOS (nodes.tcl)
    # Ejemplo: Nodo 1 (Base, Fijo), Nodo 12 (Piso superior, con masa)
    # node tag x y (recordar asignar masas y restricciones)
    # ==========================================
    # (Extraídos directamente de nodes.tcl)
    nodos_tcl = [
        (1, 12000, 20200, 7.6389, 7.6389, 0),
        (2, 15000, 20200, 7.1124, 7.1124, 0),
        (3, 18000, 20200, 3.9330375, 3.9330375, 0),
        (4, 12000, 13700, 8.1654, 8.1654, 0),
        (5, 15000, 13700, 7.1124, 7.1124, 0),
        (6, 18000, 13700, 4.309875, 4.309875, 0),
        (7, 12000, 10450, 8.1654, 8.1654, 0),
        (8, 15000, 10450, 7.1124, 7.1124, 0),
        (9, 18000, 10450, 4.309875, 4.309875, 0),
        (10, 6000, 13700, 8.1654, 8.1654, 0),
        (11, 9000, 13700, 7.1124, 7.1124, 0),
        (12, 0, 3950, 4.39104, 4.39104, 0),
        (13, 3000, 3950, 7.1124, 7.1124, 0),
        (14, 6000, 3950, 8.4763, 8.4763, 0),
        (15, 6000, 10450, 8.1654, 8.1654, 0),
        (16, 9000, 10450, 7.1124, 7.1124, 0),
        (17, 9000, 3950, 7.1124, 7.1124, 0),
        (18, 12000, 3950, 8.4763, 8.4763, 0),
        (19, 6000, 16950, 8.1654, 8.1654, 0),
        (20, 9000, 16950, 7.1124, 7.1124, 0),
        (21, 12000, 16950, 8.1654, 8.1654, 0),
        (22, 0, 20200, 3.9330375, 3.9330375, 0),
        (23, 3000, 20200, 7.1124, 7.1124, 0),
        (24, 6000, 20200, 7.6389, 7.6389, 0),
        (25, 18000, 0, 0.4580025, 0.4580025, 0),
        (26, 18000, 3950, 4.39104, 4.39104, 0),
        (27, 18000, 7200, 4.309875, 4.309875, 0),
        (28, 18000, 16950, 4.309875, 4.309875, 0),
        (29, 0, 16950, 4.309875, 4.309875, 0),
        (30, 3000, 16950, 7.1124, 7.1124, 0),
        (31, 0, 7200, 4.309875, 4.309875, 0),
        (32, 3000, 7200, 7.1124, 7.1124, 0),
        (33, 6000, 7200, 8.1654, 8.1654, 0),
        (34, 0, 13700, 4.309875, 4.309875, 0),
        (35, 3000, 13700, 7.1124, 7.1124, 0),
        (36, 0, 10450, 4.309875, 4.309875, 0),
        (37, 3000, 10450, 7.1124, 7.1124, 0),
        (38, 9000, 7200, 7.1124, 7.1124, 0),
        (39, 12000, 7200, 8.1654, 8.1654, 0),
        (40, 15000, 3950, 7.1124, 7.1124, 0),
        (41, 15000, 7200, 7.1124, 7.1124, 0),
        (42, 15000, 16950, 7.1124, 7.1124, 0),
        (43, 9000, 20200, 7.1124, 7.1124, 0),
        (44, 12000, 0, 0.8374, 0.8374, 0),
        (45, 0, 0, 0.4580025, 0.4580025, 0),
        (46, 6000, 0, 0.8374, 0.8374, 0),
    ]

    for tag, x, y, mx, my, mrz in nodos_tcl:
        # Conversión de unidades:
        # Coordenadas: TCL (mm) -> AP-GUI (m)
        x_m = float(x) / 1000.0
        y_m = float(y) / 1000.0
        
        # Masas: TCL (T) -> AP-GUI (kg)
        mx_kg = float(mx) * 1000.0
        my_kg = float(my) * 1000.0
        mrz_kg = float(mrz) * 1000.0

        n = Node(tag, x_m, y_m)
        n.mass = [mx_kg, my_kg, mrz_kg]
        
        # Asumimos que los nodos en la base (y = 0) están empotrados
        if y == 0.0:
            n.fixity = [1, 1, 1]
            
        manager.add_node(n)

    # ==========================================
    # 2. MATERIALES (materials.tcl / Sections.tcl)
    # ==========================================
    # Hormigón puro (Material 1)
    # TCL fpc: -33 MPa (N/mm2). Convertir a N/m2 (Pa) -> * 1e6
    mat_hormigon = Concrete01(tag=1, name="Hormigon_Calibrado",
        fpc=-33.0*1e6, epsc0=-0.00247, fpcu=-33.0*1e6, epsu=-0.006, rho=2500.0
    )
    manager.add_material(mat_hormigon)

    # Acero (Hysteretic - Material 2)
    # TCL tensiones en MPa -> * 1e6. Deformaciones son adimensionales.
    mat_acero = Hysteretic(tag=2, name="Acero_Calibrado",
        s1p=570*1e6, e1p=0.002875, s2p=570.1*1e6, e2p=0.055, s3p=0.0, e3p=0.09,
        s1n=-570*1e6, e1n=-0.002875, s2n=-570.1*1e6, e2n=-0.055, s3n=0.0, e3n=-0.09,
        pinch_x=0.0, pinch_y=0.0, damage1=0.0, damage2=0.0
    )
    manager.add_material(mat_acero)

    # Elastic para componente Axial P (Material 100)
    # TCL K = 1.6e5 * Ec (donde Ec=26720.6 MPa). K es Fuerza: N. N no cambia en N-m.
    K_axial = 4275303632.0 
    mat_P = Elastic(tag=100, name="P_Axial_Comun", E=K_axial)
    manager.add_material(mat_P)

    # M-phi HystereticSM (Leyes Momento-Curvatura - Secciones 1 a 14)
    # M_tcl (N*mm) -> M_ap (N*m) = / 1000
    # phi_tcl (1/mm) -> phi_ap (1/m) = * 1000
    mphi_data = [
        (16, 1, "C11", [30088475, 1.9e-06, 115584583, 3.6206e-05, 117943452, 0.000369487, 0, 0.000819634]),
        (21, 2, "C12", [101964142, 1.369e-06, 318687715, 2.3612e-05, 325191546, 0.000225416, 0, 0.000462251]),
        (30, 3, "C21", [27148361, 1.714e-06, 109625250, 3.8391e-05, 111862500, 0.000394662, 0, 0.000843212]),
        (39, 4, "C22", [71114076, 1.643e-06, 218145060, 2.8206e-05, 222597000, 0.000258044, 0, 0.000537008]),
        (48, 5, "C31", [24202394, 1.528e-06, 103600804, 3.7725e-05, 105715106, 0.000398121, 0, 0.000833827]),
        (59, 6, "C32", [61742592, 1.427e-06, 199322117, 2.7482e-05, 203389915, 0.000262106, 0, 0.000528811]),
        (62, 7, "C41", [21242464, 1.341e-06, 97491025, 3.704e-05, 99480638, 0.000401875, 0, 0.000824793]),
        (65, 8, "C42", [52391094, 1.211e-06, 180204940, 2.6731e-05, 183882592, 0.000266623, 0, 0.000521273]),
        (68, 9, "C51", [18269699, 1.153e-06, 91294044, 3.6335e-05, 93157188, 0.000405925, 0, 0.00081609]),
        (71, 10,"C52", [43057965, 9.95e-07, 160754687, 2.5945e-05, 164035395, 0.000271589, 0, 0.00051431]),
        (74, 11,"C61", [15276771, 9.65e-07, 84989752, 3.5604e-05, 86724237, 0.000410286, 0, 0.000807665]),
        (77, 12,"C62", [33753677, 7.8e-07, 140950461, 2.5116e-05, 143827001, 0.000276989, 0, 0.000507814]),
        (80, 13,"V1",  [34296290, 4.41e-07, 151702441, 1.4106e-05, 154798410, 0.00016576, 0, 0.000296272]),
        (83, 14,"V2",  [35915027, 4.43e-07, 227536561, 1.5029e-05, 232180164, 0.000168443, 0, 0.000307492])
    ]

    # ==========================================
    # 3. CREAR MATERIALES M-Phi Y SUS SECCIONES AGGREGATOR Puras
    # ==========================================
    for mat_tag, sec_tag, name, pos_points in mphi_data:
        # Extraer Momentos (ímpares) y curvaruras (pares)
        M_p = [pos_points[0], pos_points[2], pos_points[4], pos_points[6]]
        phi_p = [pos_points[1], pos_points[3], pos_points[5], pos_points[7]]

        # Conversión iterativa (N*mm -> N*m) y (1/mm -> 1/m)
        M_p_m   = [m / 1000.0 for m in M_p]
        phi_p_m = [p * 1000.0 for p in phi_p]

        # La curva negativa es simétrica según los TCL
        M_n_m   = [-m for m in M_p_m]
        phi_n_m = [-p for p in phi_p_m]

        mat_mphi = HystereticSM(tag=mat_tag, name=f"M_{name}",
            s1p=M_p_m[0], e1p=phi_p_m[0], s2p=M_p_m[1], e2p=phi_p_m[1], s3p=M_p_m[2], e3p=phi_p_m[2], s4p=M_p_m[3], e4p=phi_p_m[3],
            s1n=M_n_m[0], e1n=phi_n_m[0], s2n=M_n_m[1], e2n=phi_n_m[1], s3n=M_n_m[2], e3n=phi_n_m[2], s4n=M_n_m[3], e4n=phi_n_m[3],
            pinch_x=1.0, pinch_y=1.0, damage1=0.0, damage2=0.0, beta=0.5
        )
        manager.add_material(mat_mphi)

        # Inmediatamente creamos la Sección Aggregator (Fase 4)
        sec_agg = AggregatorSection(tag=sec_tag, name=f"Seccion_{name}")
        sec_agg.add_material(100, "P")        # El Axial genérico
        sec_agg.add_material(mat_tag, "Mz")   # El M-phi que acabamos de crear
        manager.add_section(sec_agg)

    # ==========================================
    # 4. ELEMENTOS (elements.tcl - Fase 5)
    # ==========================================
    # Mapa unificado de los TCL para asociar el nombre de la variable con (tag_seccion, Lp_en_mm)
    s_map = {
        'C11': (1, 176.5043), 'C12': (2, 218.7773), 'C21': (3, 154.5362), 'C22': (4, 182.5623),
        'C31': (5, 156.3319), 'C32': (6, 186.0492), 'C41': (7, 158.1360), 'C42': (8, 189.5286),
        'C51': (9, 159.9480), 'C52': (10, 193.0012), 'C61': (11, 161.7723), 'C62': (12, 196.4630),
        
        # Alias Columnas: Eje 3 -> Interior (como C12), Eje 4 -> Exterior (como C11)
        'C13': (2, 218.7773), 'C14': (1, 176.5043), 'C23': (4, 182.5623), 'C24': (3, 154.5362),
        'C33': (6, 186.0492), 'C34': (5, 156.3319), 'C43': (8, 189.5286), 'C44': (7, 158.1360),
        'C53': (10, 193.0012), 'C54': (9, 159.9480), 'C63': (12, 196.4630), 'C64': (11, 161.7723),
        
        # Vigas Internas y Externas (V1 es 13, V2 es 14)
        'V11': (13, 180.1390), 'V12': (14, 180.1390), 'V13': (14, 180.1390), 'V14': (14, 180.1390), 'V15': (14, 180.1390), 'V16': (13, 180.1390),
        'V21': (13, 180.1390), 'V22': (14, 180.1390), 'V23': (14, 180.1390), 'V24': (14, 180.1390), 'V25': (14, 180.1390), 'V26': (13, 180.1390),
        'V31': (13, 180.1390), 'V32': (14, 180.1390), 'V33': (14, 180.1390), 'V34': (14, 180.1390), 'V35': (14, 180.1390), 'V36': (13, 180.1390),
        'V41': (13, 180.1390), 'V42': (14, 180.1390), 'V43': (14, 180.1390), 'V44': (14, 180.1390), 'V45': (14, 180.1390), 'V46': (13, 180.1390),
        'V51': (13, 180.1390), 'V52': (14, 180.1390), 'V53': (14, 180.1390), 'V54': (14, 180.1390), 'V55': (14, 180.1390), 'V56': (13, 180.1390),
        'V61': (13, 180.1390), 'V62': (14, 180.1390), 'V63': (14, 180.1390), 'V64': (14, 180.1390), 'V65': (14, 180.1390), 'V66': (13, 180.1390),
    }

    elements_tcl = [
        # Columnas
        (49, 45, 12, 'C11'), (60, 46, 14, 'C12'), (43, 44, 18, 'C13'), (19, 25, 26, 'C14'),
        (50, 12, 31, 'C21'), (59, 14, 33, 'C22'), (44, 18, 39, 'C23'), (20, 26, 27, 'C24'),
        (51, 31, 36, 'C31'), (58, 33, 15, 'C32'), (45, 39, 7, 'C33'),  (21, 27, 9, 'C34'),
        (52, 36, 34, 'C41'), (57, 15, 10, 'C42'), (46, 7, 4, 'C43'),   (22, 9, 6, 'C44'),
        (53, 34, 29, 'C51'), (56, 10, 19, 'C52'), (47, 4, 21, 'C53'),  (23, 6, 28, 'C54'),
        (54, 29, 22, 'C61'), (55, 19, 24, 'C62'), (48, 21, 1, 'C63'),  (24, 28, 3, 'C64'),
        # Vigas
        (9,  12, 13, 'V11'), (10, 13, 14, 'V12'), (13, 14, 17, 'V13'), (14, 17, 18, 'V14'), (35, 18, 40, 'V15'), (36, 40, 26, 'V16'),
        (27, 31, 32, 'V21'), (28, 32, 33, 'V22'), (33, 33, 38, 'V23'), (34, 38, 39, 'V24'), (37, 39, 41, 'V25'), (38, 41, 27, 'V26'),
        (31, 36, 37, 'V31'), (32, 37, 15, 'V32'), (11, 15, 16, 'V33'), (12, 16, 7,  'V34'), (5,  7,  8,  'V35'), (6,  8,  9,  'V36'),
        (29, 34, 35, 'V41'), (30, 35, 10, 'V42'), (7,  10, 11, 'V43'), (8,  11, 4,  'V44'), (3,  4,  5,  'V45'), (4,  5,  6,  'V46'),
        (25, 29, 30, 'V51'), (26, 30, 19, 'V52'), (15, 19, 20, 'V53'), (16, 20, 21, 'V54'), (39, 21, 42, 'V55'), (40, 42, 28, 'V56'),
        (17, 22, 23, 'V61'), (18, 23, 24, 'V62'), (41, 24, 43, 'V63'), (42, 43, 1,  'V64'), (1,  1,  2,  'V65'), (2,  2,  3,  'V66')
    ]

    for tag, ni, nj, sec_key in elements_tcl:
        sec_tag, lp_mm = s_map[sec_key]
        
        # LP (longitud plástica): mm -> m ( / 1000)
        lp_m = lp_mm / 1000.0
        
        ele = ForceBeamColumnHinge(
            tag=tag, node_i=ni, node_j=nj, transf_tag=1,
            section_i_tag=sec_tag, lp_i=lp_m,
            section_j_tag=sec_tag, lp_j=lp_m,
            section_e_tag=sec_tag, mass_density=0.0
        )
        manager.add_element(ele)

    # ==========================================
    # 5. PATRONES DE CARGA (loads.tcl - Fase 2b)
    # ==========================================
    # Pattern 1 (Gravedad regular, fact 1.0)
    pat_grav = LoadPattern(tag=1, name="Carga_Gravitatoria", factor=1.0)
    
    # Nodal Load en el nodo 12, P_y = -100
    nl1 = NodalLoad(tag=1, node_tag=12, fx=0.0, fy=-1000.0, mz=0.0)
    pat_grav.add_load(nl1)
    
    manager.add_pattern(pat_grav)

    # ==========================================
    # 6. GUARDAR EL JSON
    # ==========================================
    save_path = "modelo_calibracion_prueba.json"
    if manager.save_project(save_path):
        print(f"¡Éxito! Abre AP-GUI y carga en 'Archivo -> Abrir': {save_path}")

if __name__ == "__main__":
    create_model()
