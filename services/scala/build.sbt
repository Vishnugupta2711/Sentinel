val scala3Version     = "3.8.4"
val zioVersion        = "2.1.17"
val zioKafkaVersion   = "2.12.0"
val protobufVersion   = "4.34.2"
val clickHouseVersion = "0.7.2"

ThisBuild / version := "0.1.0"
ThisBuild / scalaVersion := scala3Version

lazy val common = (project in file("common"))
  .settings(
    name := "sentinel-common",
    libraryDependencies ++= Seq(
      "com.google.protobuf" % "protobuf-java" % protobufVersion,
      "dev.zio"              %% "zio"                   % zioVersion,
      "dev.zio"              %% "zio-streams"           % zioVersion,
      "dev.zio"              %% "zio-kafka"             % zioKafkaVersion,
      "com.clickhouse"       %  "clickhouse-jdbc"       % clickHouseVersion,
      "dev.zio"              %% "zio-test"              % zioVersion % Test,
      "dev.zio"              %% "zio-test-sbt"          % zioVersion % Test,
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework"),
  )

lazy val streams = (project in file("streams"))
  .dependsOn(common)
  .settings(
    name := "sentinel-streams",
    libraryDependencies ++= Seq(
      "dev.zio"     %% "zio"         % zioVersion,
      "dev.zio"     %% "zio-streams" % zioVersion,
      "dev.zio"     %% "zio-kafka"   % zioKafkaVersion,
      "dev.zio"     %% "zio-test"    % zioVersion % Test,
      "dev.zio"     %% "zio-test-sbt"% zioVersion % Test,
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework"),
  )

lazy val cep = (project in file("cep"))
  .dependsOn(common)
  .settings(
    name := "sentinel-cep",
    libraryDependencies ++= Seq(
      "dev.zio"     %% "zio"         % zioVersion,
      "dev.zio"     %% "zio-streams" % zioVersion,
      "dev.zio"     %% "zio-kafka"   % zioKafkaVersion,
      "dev.zio"     %% "zio-test"    % zioVersion % Test,
      "dev.zio"     %% "zio-test-sbt"% zioVersion % Test,
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework"),
  )

lazy val sink = (project in file("sink"))
  .dependsOn(common)
  .settings(
    name := "sentinel-sink",
    libraryDependencies ++= Seq(
      "dev.zio"     %% "zio"         % zioVersion,
      "dev.zio"     %% "zio-streams" % zioVersion,
      "dev.zio"     %% "zio-kafka"   % zioKafkaVersion,
      "com.clickhouse" % "clickhouse-jdbc" % clickHouseVersion,
      "dev.zio"     %% "zio-test"    % zioVersion % Test,
      "dev.zio"     %% "zio-test-sbt"% zioVersion % Test,
    ),
    testFrameworks += new TestFramework("zio.test.sbt.ZTestFramework"),
  )

lazy val root = (project in file("."))
  .aggregate(common, streams, cep, sink)
