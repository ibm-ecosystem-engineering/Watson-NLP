package com.build.labs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class WnlpRestAppApplication {

	public static void main(String[] args) {
		SpringApplication.run(WnlpRestAppApplication.class, args);
	}

}
