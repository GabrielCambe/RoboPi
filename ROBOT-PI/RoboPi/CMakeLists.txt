add_definitions( -lwiringPi  )
target_link_libraries(${PROJECT_NAME}_class ${wiringPi_LIB}  -lcrypt -lrt)