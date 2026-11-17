import java.awt.geom.CubicCurve2D;
import java.awt.geom.Rectangle2D;
import java.io.BufferedReader;
import java.io.InputStreamReader;

/**
 * Runs java.awt.geom.CubicCurve2D.getBounds2D over a batch of curves.
 *
 * Input: one curve per line, eight numbers separated by spaces.
 * Output: one line per curve, "xmin ymin xmax ymax".
 */
public class Bounds {
    public static void main(String[] args) throws Exception {
        if (args.length > 0 && args[0].equals("--version")) {
            System.out.println(System.getProperty("java.version"));
            return;
        }
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            String[] f = line.trim().split(" ");
            if (f.length != 8) {
                continue;
            }
            double[] c = new double[8];
            for (int i = 0; i < 8; i++) {
                c[i] = Double.parseDouble(f[i]);
            }
            Rectangle2D r = new CubicCurve2D.Double(
                c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]).getBounds2D();
            out.append(r.getMinX()).append(' ').append(r.getMinY()).append(' ')
               .append(r.getMaxX()).append(' ').append(r.getMaxY()).append('\n');
        }
        System.out.print(out);
    }
}
