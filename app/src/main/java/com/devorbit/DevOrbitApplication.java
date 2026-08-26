package com.devorbit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DevOrbitApplication {

    private static final Logger log = LoggerFactory.getLogger(DevOrbitApplication.class);

    public static void main(String[] args) {
        SpringApplication.run(DevOrbitApplication.class, args);
        log.info("=================================================");
        log.info("DevOrbit Campus Issue Management Application Started");
        log.info("Ready to accept requests on default port 8080");
        log.info("=================================================");
    }
}
