pipeline {

    agent any

    /******************************************************************
     * Opciones generales del pipeline.
     * Se anaden marcas de tiempo y soporte para colores ANSI.
     * Se deshabilita el checkout automatico para controlar
     * explicitamente la etapa "Get Code".
     ******************************************************************/
    options {
        timestamps()
        ansiColor('xterm')
        skipDefaultCheckout(true)
    }

    /******************************************************************
     * Variables globales del Pipeline.
     ******************************************************************/
    environment {

        //Entorno Actual.
        //CONFIG_ENV = "${env.BRANCH_NAME == 'master' ? 'production' : 'staging'}"
        CONFIG_ENV = 'production'

        // Carpeta de reportes para publicacion de resultados.
        REPORTS = 'reports'

    	// Entorno virtual preparado previamente en Jenkins.
    	VENV = "/var/lib/jenkins/.venv/bin"

    }

    stages {

        /**************************************************************
         * Descarga el codigo fuente desde GitHub.
         **************************************************************/
        stage('Get Code') {

            steps {
                // Limpia completamente el workspace para evitar residuos
                // de ejecuciones anteriores.
                cleanWs()
                     
                // Descarga la rama del repositorio.        
                git branch: 'master',
                    credentialsId: 'github-pat',
                    url: 'https://github.com/guarrior-labs/todo-list-aws.git'
            }
        }

        /*****************************************************************
         * Inicializa el pipeline (Despues de descargar archivos limpios).
         *****************************************************************/
        stage('Initializa') {

            steps {

                echo '==========================================='
                echo 'CP1.4 - RETO 2'
                echo 'Pipeline de Despliegue Continuo (CD)'
                echo 'Entorno de despliegue: PRODUCTION'
                echo '==========================================='

                script {

                    def config = readTOML file: 'samconfig.toml'
                    def envConfig = config[env.CONFIG_ENV].deploy.parameters

                    env.REGION              = envConfig.region.toString()
                    env.AWS_REGION          = env.REGION
                    env.AWS_DEFAULT_REGION  = env.REGION

                    env.STACK_NAME          = envConfig.stack_name.toString()
/*
                  env.S3_PREFIX           = envConfig.s3_prefix.toString()
                    env.CAPABILITIES        = envConfig.capabilities.toString()
                    env.PARAMETER_OVERRIDES = envConfig.parameter_overrides.toString()      

                    echo config.toString()
                    echo "REGION             = '${env.REGION}'"
                    echo "AWS_REGION         = '${env.REGION}'"
                    echo "AWS_DEFAULT_REGION = '${env.REGION}'"
                    echo "STACK_NAME         = '${env.STACK_NAME}'"
                    echo "CONFIG_ENV         = '${env.CONFIG_ENV}'"                      
*/
                }

            }

        }
        /**************************************************************
         * Construye, valida y despliega la aplicacion Serverless.
         * Tras un despliegue correcto obtiene dinamicamente la URL
         * publicada por CloudFormation.
         **************************************************************/
        stage('Despliegue') {

            steps {

                script {
                
                    sh """                    
                    ############################################################
                    # sam build
                    # Construye la aplicacion Serverless.
                    #
                    # Parametros:
                    #   (sin parametros)
                    #   build: Compila la aplicacion, resuelve dependencias y
                    #   genera los artefactos en .aws-sam para el despliegue.
                    ############################################################
                    sam build

                    ############################################################
                    # sam validate
                    # Valida la sintaxis y estructura del template SAM antes
                    # del despliegue.
                    #
                    # Parametros:
                    #   (sin parametros)
                    #   validate: Comprueba que template.yaml sea valido.
                    ############################################################                   
                    sam validate

                    ############################################################
                    # sam deploy
                    # Despliega la aplicacion en AWS mediante CloudFormation.
                    #
                    # Parametros:
                    #   --config-env ${CONFIG_ENV}
                    #       Selecciona la configuracion del entorno definido
                    #       en samconfig.toml (staging o production).
                    #
                    #   --resolve-s3
                    #       Crea o reutiliza automaticamente un bucket S3 para
                    #       almacenar los artefactos del despliegue.
                    #
                    #   --no-confirm-changeset
                    #       Evita solicitar confirmacion interactiva antes de
                    #       aplicar los cambios, permitiendo la automatizacion.
                    #
                    #   --no-fail-on-empty-changeset
                    #       Si no existen cambios respecto al despliegue
                    #       anterior, finaliza correctamente sin marcar error.
                    ############################################################
                    sam deploy \
                        --config-env ${CONFIG_ENV} \
                        --resolve-s3 \
                        --no-confirm-changeset \
                        --no-fail-on-empty-changeset
                        """

                     env.API_URL = sh(
                        returnStdout: true,
                        script: """

                       
                        aws cloudformation describe-stacks \
                            --region ${env.REGION} \
                            --stack-name ${env.STACK_NAME} \
                            --query "Stacks[0].Outputs[0].OutputValue" \
                            --output text
                        """                       
                    ).trim()
                    //echo ">>>> ${apiUrl} <<<<"
                    //env.API_URL = apiUrl
                    //echo "ENV=${env.API_URL}"
                }
            }
        }

        /**************************************************************
         * Ejecuta las pruebas de analisis estatico.
         *
         * La etapa solo falla si los comandos no pueden
         * ejecutarse correctamente.
         **************************************************************/
        stage('Staticas') {

            //Pruebas solo en Staging (develop).
            when {
                environment name: 'CONFIG_ENV', value: 'staging'
            }
            
            steps {

                sh '''

                    ##################################################################################################
                    # mkdir : crea directorios.
                    # -p    : crea tambien los directorios padre si no existen y no falla si el directorio ya existe.
                    # ${REPORTS} : variable de entorno que contiene la ruta donde se almacenaran los informes.
                    ###################################################################################################
                    mkdir -p ${REPORTS}

                    #####################################################################
                    # FLAKE8
                    #
                    # ${VENV}/flake8     Ejecuta Flake8 desde el entorno virtual.
                    # src               Directorio del codigo fuente a analizar.
                    # --statistics      Muestra un resumen con el numero de incidencias
                    #                   encontradas por tipo de error.
                    # --tee             Envia la salida simultaneamente a la consola y
                    #                   al fichero indicado con --output-file.
                    # --output-file     Guarda el informe generado para su publicacion
                    #                   posterior desde Jenkins.
                    # --exit-zero       Devuelve codigo de salida 0 aunque existan
                    #                   incidencias, permitiendo que la etapa solo falle
                    #                   si el comando no puede ejecutarse.
                    #####################################################################

                    echo "========== FLAKE8 =========="
                    ${VENV}/flake8 src \
                        --statistics \
                        --tee \
                        --output-file ${REPORTS}/flake8.txt \
                        --exit-zero

                    #####################################################################
                    # BANDIT
                    #
                    # ${VENV}/bandit    Ejecuta Bandit desde el entorno virtual.
                    # -r src            Analiza recursivamente todo el codigo contenido
                    #                   en el directorio src.
                    # -f txt            Genera el informe en formato de texto plano.
                    # -o                Guarda el resultado del analisis en el fichero
                    #                   especificado para su posterior publicacion.
                    ######################################################################
                    echo "========== BANDIT =========="
                    ${VENV}/bandit \
                        -r src \
                        -f txt \
                        -o ${REPORTS}/bandit.txt
                '''

            }

        }

        /**************************************************************
         * Publica resultados de pruebas estaticas,
         * solo cuando sea pipeline de staging.
         **************************************************************/
        stage('informes Estaticas') {

            when {
                environment name: 'CONFIG_ENV', value: 'staging'
            }

            steps {

                archiveArtifacts(
                    artifacts: "${REPORTS}/*",
                    fingerprint: true,
                    allowEmptyArchive: true
                )

            }

        }

        /***************************************
         * Ejecuta pruebas integracion sobre API
         * desplegada.
         ***************************************/
        stage('Integracion') {

            steps {
                
                //"BASE_URL" No modifica entorno global y solo existe dentro del bloque
                withEnv(["BASE_URL=${env.API_URL}"]) {

                    script {
                        //################################################################################
                        //# pytestCmd  -> Determina si ejecuta pruebas completas o solo lectura,
                        //# (staging vs production).
                        //#
                        //# ${VENV}/bin/pytest          -> Ejecuta Pytest desde el entorno virtual.
                        //# test/integration/todoApiTest.py -> Ruta con las pruebas de integracion.
                        //# -k "test_api_gettodo or test_api_listtodos" -> Especifica metodos a ejecutar.
                        //# -v  -> (verbose) Activa Log con metodos seleccionados/no-seleccionados/.
                        //# -ra -> Resumen mas completo al final del log                        
                        //# --junitxml=result-rest.xml  -> Genera un informe JUnit compatible con Jenkins.
                        //#################################################################################
                        def pytestCmd = """
                            ${VENV}/pytest \
                            test/integration/todoApiTest.py \
                            -v \
                            -ra \
                            --junitxml=result-rest.xml
                        """

                        if (env.CONFIG_ENV == "production") {
                            pytestCmd = """
                                ${VENV}/pytest \
                                test/integration/todoApiTest.py \
                                -k "test_api_gettodo or test_api_listtodos" \
                                -v \
                                -ra \
                                --junitxml=result-rest.xml
                            """
                        }
                    sh pytestCmd    
                    }

                }

            }

        }
        /************************************************
         * Promueve version integrando develop en master.
         *
         * Requiere credenciales de escritura sobre GitHub.
         *************************************************/
        stage('Promover') {

            when {
                //Merge solo en Staging (develop).
                environment name: 'CONFIG_ENV', value: 'staging'
            }

            steps {
                
                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-pat',
                        usernameVariable: 'GITHUB_USER',
                        passwordVariable: 'GITHUB_PAT'
                    )
                ]) 
                
                {
                sh '''
                    # Cambia a la rama master
                    git checkout master

                    # Actualiza la rama local con el estado del remoto
                    git fetch origin
                    git reset --hard origin/master

                    # Integra los cambios validados de develop
                    git merge origin/develop

                    # Publica la nueva version en el repositorio remoto
                    git push https://${GITHUB_USER}:${GITHUB_PAT}@github.com/guarrior-labs/todo-list-aws.git master

                '''
                }
            }
        }

    }

    /******************************************************************
     * Publica los informes generados durante la ejecucion.
     ******************************************************************/
    post {

        always {

            junit(
                allowEmptyResults: true,
                testResults: 'result-rest.xml'
            )

        }

    }

}
