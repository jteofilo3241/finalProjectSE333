import java.lang.reflect.Field;
import java.util.List;
import org.apache.commons.lang3.reflect.FieldUtils;

public class InspectFields {
    public static void main(String[] args) throws Exception {
        Class<?> pc = Class.forName("org.apache.commons.lang3.reflect.testbed.PublicChild");
        Class<?> parent = pc.getSuperclass();
        System.out.println("PublicChild declared fields:");
        for (Field f : pc.getDeclaredFields()) {
            System.out.println("  " + f.getName() + " (modifiers=" + f.getModifiers() + ")");
        }
        System.out.println("Parent declared fields:");
        for (Field f : parent.getDeclaredFields()) {
            System.out.println("  " + f.getName() + " (modifiers=" + f.getModifiers() + ")");
        }
        System.out.println("FieldUtils.getAllFieldsList size and names:");
        List<Field> all = FieldUtils.getAllFieldsList(pc);
        System.out.println(" size=" + all.size());
        for (Field f : all) System.out.println("  " + f.getName() + " (" + f.getDeclaringClass().getSimpleName() + ")");
    }
}