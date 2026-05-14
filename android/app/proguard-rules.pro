# Add project specific ProGuard rules here.

# Ktor
-keep class io.ktor.** { *; }
-keepclassmembers class io.ktor.** { *; }
-dontwarn io.ktor.**

# Kotlinx Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.liksoft.pharmalert.**$$serializer { *; }
-keepclassmembers class com.liksoft.pharmalert.** {
    *** Companion;
}
-keepclasseswithmembers class com.liksoft.pharmalert.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# Data classes (DTOs)
-keep class com.liksoft.pharmalert.data.dto.** { *; }