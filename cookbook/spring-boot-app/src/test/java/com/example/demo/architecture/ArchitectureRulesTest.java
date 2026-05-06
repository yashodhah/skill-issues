package com.example.demo.architecture;

import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RestController;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noFields;

@AnalyzeClasses(packages = "com.example.demo")
class ArchitectureRulesTest {

    // JAVA-002: No @Autowired on fields — use constructor injection
    @ArchTest
    static final ArchRule noFieldInjection = noFields()
        .should().beAnnotatedWith(Autowired.class)
        .because("JAVA-002: Use constructor injection — see .github/skills/java-patterns/SKILL.md");

    // ARCH-001: Controllers must not access repositories directly — must go through a service
    @ArchTest
    static final ArchRule controllersDoNotAccessRepositories = noClasses()
        .that().areAnnotatedWith(RestController.class)
        .or().areAnnotatedWith(Controller.class)
        .should().dependOnClassesThat().areAnnotatedWith(Repository.class)
        .because("ARCH-001: Controllers must not access repositories directly — route through a @Service")
        .allowEmptyShould(true);

    // ARCH-002: @Service classes must live in a ..service.. package
    @ArchTest
    static final ArchRule serviceClassesInServicePackage = classes()
        .that().areAnnotatedWith(Service.class)
        .should().resideInAPackage("..service..")
        .because("ARCH-002: @Service classes must live in a ..service.. package")
        .allowEmptyShould(true);
}
