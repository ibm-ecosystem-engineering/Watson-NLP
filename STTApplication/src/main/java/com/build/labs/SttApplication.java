package com.build.labs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class SttApplication {

	public static void main(String[] args) {
		SpringApplication.run(SttApplication.class, args);
	}

}
