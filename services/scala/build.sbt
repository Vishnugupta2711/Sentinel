val scala3Version = "3.8.4"
val zioVersion = "2.1.17"
val zioKafkaVersion = "2.12.0"

ThisBuild / version := "0.1.0"
ThisBuild / scalaVersion := scala3Version

lazy val streams = (project in file("streams"))
  .settings(
    name := "sentinel-streams",
    libraryDependencies ++= Seq(
      "dev.zio" %% "zio" % zioVersion,
      "dev.zio" %% "zio-streams" % zioVersion,
      "dev.zio" %% "zio-kafka" % zioKafkaVersion,
      "dev.zio" %% "zio-test" % zioVersion % Test,
      "dev.zio" %% "zio-test-sbt" % zioVersion % Test
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework")
  )

lazy val cep = (project in file("cep"))
  .settings(
    name := "sentinel-cep",
    libraryDependencies ++= Seq(
      "dev.zio" %% "zio" % zioVersion,
      "dev.zio" %% "zio-streams" % zioVersion,
      "dev.zio" %% "zio-kafka" % zioKafkaVersion,
      "dev.zio" %% "zio-test" % zioVersion % Test,
      "dev.zio" %% "zio-test-sbt" % zioVersion % Test
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework")
  )

lazy val sink = (project in file("sink"))
  .settings(
    name := "sentinel-sink",
    libraryDependencies ++= Seq(
      "dev.zio" %% "zio" % zioVersion,
      "dev.zio" %% "zio-streams" % zioVersion,
      "dev.zio" %% "zio-kafka" % zioKafkaVersion,
      "dev.zio" %% "zio-test" % zioVersion % Test,
      "dev.zio" %% "zio-test-sbt" % zioVersion % Test
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework")
  )

lazy val root = (project in file("."))
  .aggregate(streams, cep, sink)
