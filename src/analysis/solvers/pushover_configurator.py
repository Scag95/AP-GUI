import openseespy.opensees as ops

class PushoverConfigurator:
    def __init__(self, builder, debug_file=None):
        self.builder = builder
        self.debug_file = debug_file
        
        # Guardamos los parámetros originales para restaurarlos tras los fallbacks
        self.base_tol = 1e-06
        self.base_iter = 100

    def setup_static_analysis(self, control_node_tag, incr_disp):
        """
        Configura el entorno de OpenSees para el paso estático del Pushover.
        Centraliza los comandos que rigen el motor matemático.
        """
        self.builder.log_command('wipeAnalysis')
        self.builder.log_command('system', 'UmfPack') 
        self.builder.log_command('numberer', 'RCM')   
        self.builder.log_command('constraints', 'Transformation') 
        
        # Integrador de control de desplazamiento
        self.builder.log_command('integrator', 'DisplacementControl', control_node_tag, 1, incr_disp)
        
        # Criterio de convergencia y algoritmo principal (KrylovNewton)
        self.builder.log_command('test', 'NormDispIncr', self.base_tol, self.base_iter)
        self.builder.log_command('algorithm', 'KrylovNewton')
        self.builder.log_command('analysis', 'Static')


    def run_static_step_with_fallback(self):
        """
        Intenta resolver un paso estático. Si el algoritmo principal falla, 
        intenta iterativamente con algoritmos más robustos según las mejores prácticas.
        """
        # Intento primario (KrylovNewton)
        ok = ops.analyze(1)
        if ok == 0:
            return ok
            
        print("[Configurator] Convergencia falló con KrylovNewton, intentando algoritmos de respaldo...")
        
        # Respaldo 1: NewtonLineSearch 0.8
        if ok != 0:
            print(" -> Intentando NewtonWithLineSearch 0.8 ...")
            ops.algorithm('NewtonLineSearch', 0.8)
            ok = ops.analyze(1)
            if ok == 0: 
                print(" -> ¡Éxito! Restaurando a KrylovNewton.")
            
            # Restaurar estado original pase lo que pase
            ops.test('NormDispIncr', self.base_tol, self.base_iter)
            ops.algorithm('KrylovNewton')

        # Respaldo 2: NewtonLineSearch 0.6
        if ok != 0:
            print(" -> Intentando NewtonWithLineSearch 0.6 ...")
            ops.algorithm('NewtonLineSearch', 0.6)
            ok = ops.analyze(1)
            if ok == 0: 
                print(" -> ¡Éxito! Restaurando a KrylovNewton.")
            
            # Restaurar estado original
            ops.test('NormDispIncr', self.base_tol, self.base_iter)
            ops.algorithm('KrylovNewton')
            
        # Respaldo 3: Broyden
        if ok != 0:
            print(" -> Intentando Broyden 20 ...")
            ops.algorithm('Broyden', 20)
            ok = ops.analyze(1)
            if ok == 0: 
                print(" -> ¡Éxito! Restaurando a KrylovNewton.")
            
            # Restaurar estado original
            ops.test('NormDispIncr', self.base_tol, self.base_iter)
            ops.algorithm('KrylovNewton')

        # Respaldo 4: ModifiedNewton con Tangente Inicial
        if ok != 0:
            print(" -> Intentando ModifiedNewton con Tangente Inicial ...")
            # OpenSeesPy espera el flag '-initial' para la tangente inicial
            ops.algorithm('ModifiedNewton', '-initial')
            ok = ops.analyze(1)
            if ok == 0: 
                print(" -> ¡Éxito! Restaurando a KrylovNewton.")
            
            # Restaurar estado original
            ops.test('NormDispIncr', self.base_tol, self.base_iter)
            ops.algorithm('KrylovNewton')

        # Respaldo 5: Newton con Tangente Inicial
        if ok != 0:
            print(" -> Intentando Newton con Tangente Inicial ...")
            # OpenSeesPy espera el flag '-initial'
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1)
            if ok == 0: 
                print(" -> ¡Éxito! Restaurando a KrylovNewton.")
            
            # Restaurar estado original
            ops.test('NormDispIncr', self.base_tol, self.base_iter)
            ops.algorithm('KrylovNewton')
        
        return ok
